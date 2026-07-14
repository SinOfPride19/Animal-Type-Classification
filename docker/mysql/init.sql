-- ============================================================
-- ATC System — MySQL Database Schema
-- Animal Type Classification (Rashtriya Gokul Mission)
-- ============================================================

CREATE DATABASE IF NOT EXISTS atc_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE atc_db;

-- ── Animals ───────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS animals (
    id           CHAR(36)     NOT NULL PRIMARY KEY,
    tag_number   VARCHAR(50)  UNIQUE,
    name         VARCHAR(100),
    breed        VARCHAR(100),
    age_years    FLOAT,
    sex          ENUM('male','female','unknown') DEFAULT 'unknown',
    owner_name   VARCHAR(150),
    owner_contact VARCHAR(50),
    location     VARCHAR(200),
    notes        TEXT,
    created_at   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_tag_number (tag_number),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── Images ────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS images (
    id            CHAR(36)    NOT NULL PRIMARY KEY,
    animal_id     CHAR(36)    NOT NULL,
    filename      VARCHAR(255) NOT NULL,
    filepath      VARCHAR(500) NOT NULL,
    original_name VARCHAR(255),
    file_size     INT,
    width         INT,
    height        INT,
    mime_type     VARCHAR(50),
    is_processed  BOOLEAN     DEFAULT FALSE,
    created_at    DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_images_animal FOREIGN KEY (animal_id)
        REFERENCES animals(id) ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX idx_images_animal (animal_id),
    INDEX idx_images_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── Classifications ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS classifications (
    id                   CHAR(36)    NOT NULL PRIMARY KEY,
    animal_id            CHAR(36)    NOT NULL,
    image_id             CHAR(36)    NOT NULL UNIQUE,

    -- Classifier output
    predicted_class      ENUM('cow','buffalo','unknown') NOT NULL DEFAULT 'unknown',
    confidence           FLOAT       NOT NULL DEFAULT 0.0,

    -- Detection (YOLOv8)
    detection_confidence FLOAT,
    bbox_x1              FLOAT,
    bbox_y1              FLOAT,
    bbox_x2              FLOAT,
    bbox_y2              FLOAT,

    -- Morphometric measurements (pixels)
    body_length_px       FLOAT,
    height_px            FLOAT,
    chest_width_px       FLOAT,
    chest_girth_px       FLOAT,
    body_depth_px        FLOAT,
    rump_width_px        FLOAT,
    pixel_per_cm         FLOAT,

    -- Normalised measurements (cm)
    body_length_cm       FLOAT,
    height_cm            FLOAT,
    chest_girth_cm       FLOAT,
    body_depth_cm        FLOAT,
    rump_width_cm        FLOAT,

    -- Metadata
    processing_time_ms   FLOAT,
    pipeline_version     VARCHAR(20) DEFAULT '1.0',
    error_message        TEXT,
    status               ENUM('pending','processing','completed','failed') DEFAULT 'pending',

    created_at           DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at           DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_clf_animal FOREIGN KEY (animal_id)
        REFERENCES animals(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_clf_image FOREIGN KEY (image_id)
        REFERENCES images(id) ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX idx_clf_animal    (animal_id),
    INDEX idx_clf_status    (status),
    INDEX idx_clf_class     (predicted_class),
    INDEX idx_clf_created   (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── Scores ────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS scores (
    id                    CHAR(36)    NOT NULL PRIMARY KEY,
    classification_id     CHAR(36)    NOT NULL UNIQUE,

    -- Component scores (0-100 each)
    body_length_score     FLOAT       NOT NULL DEFAULT 0.0,
    height_score          FLOAT       NOT NULL DEFAULT 0.0,
    chest_girth_score     FLOAT       NOT NULL DEFAULT 0.0,
    rump_angle_score      FLOAT       NOT NULL DEFAULT 0.0,
    rump_width_score      FLOAT       NOT NULL DEFAULT 0.0,
    body_depth_score      FLOAT       NOT NULL DEFAULT 0.0,
    dairy_character_score FLOAT       NOT NULL DEFAULT 0.0,
    feet_legs_score       FLOAT       NOT NULL DEFAULT 0.0,
    udder_score           FLOAT       NOT NULL DEFAULT 0.0,

    -- Final weighted ATC score
    final_score           FLOAT       NOT NULL DEFAULT 0.0,
    grade                 ENUM('Excellent','Good Plus','Good','Average') NOT NULL DEFAULT 'Average',

    created_at            DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_scores_clf FOREIGN KEY (classification_id)
        REFERENCES classifications(id) ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX idx_scores_grade      (grade),
    INDEX idx_scores_final      (final_score),
    INDEX idx_scores_created    (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ── Sample seed data (for testing UI without actual ML) ───────────────────────
INSERT IGNORE INTO animals (id, tag_number, name, breed, age_years, sex, owner_name, location) VALUES
  ('a0000001-0000-0000-0000-000000000001', 'GJ-2024-001', 'Lakshmi', 'Gir',     5.0, 'female', 'Ramesh Patel',   'Anand, Gujarat'),
  ('a0000001-0000-0000-0000-000000000002', 'RJ-2024-002', 'Nandini', 'Sahiwal', 4.5, 'female', 'Suresh Kumar',   'Jaipur, Rajasthan'),
  ('a0000001-0000-0000-0000-000000000003', 'MH-2024-003', 'Gauri',   'Murrah',  6.0, 'female', 'Vijay Shinde',   'Pune, Maharashtra');

SELECT 'ATC System schema initialized successfully.' AS status;
