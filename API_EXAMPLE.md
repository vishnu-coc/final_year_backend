# API Usage Examples

## `/analyze` Endpoint Example

### Example 1: Analyze PDF without a specific question

**Request in Postman:**
- **Method:** `POST`
- **URL:** `http://localhost:8000/analyze`
- **Body Type:** `form-data`
- **Fields:**
  - `file` (File type): Upload your PDF file (e.g., `legal_document.pdf`)
  - `question` (Text type): Leave empty or omit

**Example Response:**
```json
{
  "filename": "legal_document.pdf",
  "document_stats": {
    "total_pages": 15,
    "total_characters": 25000,
    "total_words": 4200,
    "total_sentences": 210,
    "total_paragraphs": 45,
    "estimated_reading_time_minutes": 21.0
  },
  "key_points": "• The document outlines privacy policy requirements\n• Users must consent to data collection\n• Data retention period is 2 years\n• Users have right to request data deletion\n• GDPR compliance is mandatory\n• Security measures include encryption\n• Third-party sharing requires explicit consent",
  "question": null,
  "analysis": "Based on the key points extracted, this document is a privacy policy focusing on data protection and user rights. The policy emphasizes GDPR compliance, requiring explicit user consent for data collection and sharing. Key protections include the right to data deletion and mandatory encryption for security. The 2-year data retention period suggests a structured approach to data management. The emphasis on explicit consent for third-party sharing indicates a commitment to transparency and user control over personal information.",
  "extraction_summary": {
    "text_chunks_extracted": 15,
    "text_length": 25000
  }
}
```

---

### Example 2: Analyze PDF with a specific question

**Request in Postman:**
- **Method:** `POST`
- **URL:** `http://localhost:8000/analyze`
- **Body Type:** `form-data`
- **Fields:**
  - `file` (File type): Upload your PDF file (e.g., `contract.pdf`)
  - `question` (Text type): `"What are the main obligations of the parties?"`

**Example Response:**
```json
{
  "filename": "contract.pdf",
  "document_stats": {
    "total_pages": 8,
    "total_characters": 12000,
    "total_words": 2000,
    "total_sentences": 95,
    "total_paragraphs": 22,
    "estimated_reading_time_minutes": 10.0
  },
  "key_points": "• Party A must deliver goods within 30 days\n• Party B must make payment within 15 days of delivery\n• Quality standards must meet ISO 9001\n• Both parties must maintain confidentiality\n• Disputes resolved through arbitration\n• Force majeure clause included\n• Contract term is 12 months",
  "question": "What are the main obligations of the parties?",
  "analysis": "Based on the extracted key points, the main obligations of the parties are:\n\n**Party A's Obligations:**\n- Deliver goods within 30 days of the agreement\n- Ensure goods meet ISO 9001 quality standards\n- Maintain confidentiality of shared information\n\n**Party B's Obligations:**\n- Make payment within 15 days of receiving the delivery\n- Maintain confidentiality as specified in the contract\n- Adhere to the 12-month contract term\n\nBoth parties are also subject to the force majeure clause and agree to resolve disputes through arbitration, indicating a structured approach to managing potential conflicts.",
  "extraction_summary": {
    "text_chunks_extracted": 8,
    "text_length": 12000
  }
}
```

---

### Example 3: Using cURL

```bash
curl -X POST "http://localhost:8000/analyze" \
  -F "file=@/path/to/your/document.pdf" \
  -F "question=What are the key takeaways?"
```

Or without a question:
```bash
curl -X POST "http://localhost:8000/analyze" \
  -F "file=@/path/to/your/document.pdf"
```

---

### Example 4: Using Python requests

```python
import requests

url = "http://localhost:8000/analyze"

# With a question
files = {"file": open("document.pdf", "rb")}
data = {"question": "What are the main points discussed?"}

response = requests.post(url, files=files, data=data)
result = response.json()

print("Key Points:", result["key_points"])
print("\nAnalysis:", result["analysis"])
```

```python
# Without a question (just analysis)
files = {"file": open("document.pdf", "rb")}

response = requests.post(url, files=files)
result = response.json()

print("Key Points:", result["key_points"])
print("\nAnalysis:", result["analysis"])
```

---

### Example 5: Using JavaScript/React

```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]); // file from input element
formData.append('question', 'What is this document about?');

fetch('http://localhost:8000/analyze', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => {
  console.log('Key Points:', data.key_points);
  console.log('Analysis:', data.analysis);
})
.catch(error => console.error('Error:', error));
```

---

## Summary

The `/analyze` endpoint:
1. **Extracts text** from the uploaded PDF
2. **Extracts key points** using Groq API
3. **Analyzes key points** using Groq API (or answers your question)
4. Returns structured response with key points and analysis

The response always includes:
- Document statistics (pages, words, etc.)
- Extracted key points
- AI analysis of the key points
- Your question (if provided)
