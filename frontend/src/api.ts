// classify image (backend call)
export async function classifyAnimal(file: File) {
  const form = new FormData();
  form.append("file", file);

  const res = await fetch("http://127.0.0.1:8000/classify", {
    method: "POST",
    body: form,
  });

  if (!res.ok) {
    throw new Error("Backend error");
  }

  return res.json();
}


export function saveRecord(record: any) {
  const existing = JSON.parse(localStorage.getItem("records") || "[]");

  // ensure image persists (blob URL issue fix)
  const safeRecord = {
    ...record,
    image_url: record.image_url || ""
  };

  existing.unshift(safeRecord);
  localStorage.setItem("records", JSON.stringify(existing));
}


// GET RECORDS
export function getRecords(): any[] {
  try {
    return JSON.parse(localStorage.getItem("records") || "[]");
  } catch {
    return [];
  }
}


// OPTIONAL: CLEAR DATA (useful for testing)
export function clearRecords() {
  localStorage.removeItem("records");
}