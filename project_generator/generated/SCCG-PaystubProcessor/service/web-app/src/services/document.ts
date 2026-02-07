import { apiRequest } from './api';

export interface DocumentResult {
  documentId: string;
  extractedFields: Record<string, string>;
  confidence: number;
}

export async function processDocument(file: File): Promise<DocumentResult> {
  const formData = new FormData();
  formData.append('document', file);

  return apiRequest<DocumentResult>('/process', {
    method: 'POST',
    body: formData,
  });
}

export async function getDocument(documentId: string): Promise<DocumentResult> {
  return apiRequest<DocumentResult>(`/documents/${documentId}`);
}
