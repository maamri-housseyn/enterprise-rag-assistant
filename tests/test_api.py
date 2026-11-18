from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_create_document():
    payload = {
        "filename": "test_api_document.pdf",
        "file_path": "data/test_api_document.pdf"
    }

    response = client.post("/documents/", json=payload)

    assert response.status_code == 201

    data = response.json()

    assert data["id"] is not None
    assert data["filename"] == "test_api_document.pdf"
    assert data["file_path"] == "data/test_api_document.pdf"
    assert "created_at" in data    

def test_get_document():
    # 1. Create a document
    payload = {
        "filename": "document_to_retrieve.pdf",
        "file_path": "data/document_to_retrieve.pdf"
    }

    create_response = client.post("/documents/", json=payload)

    assert create_response.status_code == 201

    document_id = create_response.json()["id"]

    # 2. Retrieve the document
    response = client.get(f"/documents/{document_id}")

    assert response.status_code == 200
    assert response.json()["id"] == document_id
    assert response.json()["filename"] == "document_to_retrieve.pdf"

def test_update_document():
    # 1. Create a document
    payload = {
        "filename": "document_before_update.pdf",
        "file_path": "data/document_before_update.pdf"
    }

    create_response = client.post("/documents/", json=payload)

    assert create_response.status_code == 201

    document_id = create_response.json()["id"]

    # 2. Update the document
    update_payload = {
        "filename": "document_after_update.pdf"
    }

    response = client.put(
        f"/documents/{document_id}",
        json=update_payload
    )

    # 3. Verify the update
    assert response.status_code == 200
    assert response.json()["id"] == document_id
    assert response.json()["filename"] == "document_after_update.pdf"
    assert response.json()["file_path"] == "data/document_before_update.pdf"

def test_delete_document():
    # 1. Create a document
    payload = {
        "filename": "document_to_delete.pdf",
        "file_path": "data/document_to_delete.pdf"
    }

    create_response = client.post("/documents/", json=payload)

    assert create_response.status_code == 201

    document_id = create_response.json()["id"]

    # 2. Delete the document
    response = client.delete(f"/documents/{document_id}")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Document deleted successfully"
    }

    # 3. Verify that the document no longer exists
    get_response = client.get(f"/documents/{document_id}")

    assert get_response.status_code == 404

def test_get_nonexistent_document():
    response = client.get("/documents/999999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Document not found"
    }

def test_update_nonexistent_document():
    payload = {
        "filename": "new_filename.pdf"
    }

    response = client.put(
        "/documents/999999",
        json=payload
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Document not found"
    }

def test_delete_nonexistent_document():
    response = client.delete("/documents/999999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Document not found"
    }

def test_create_document_with_invalid_data():
    # Missing the required file_path field
    payload = {
        "filename": "invalid_document.pdf"
    }

    response = client.post("/documents/", json=payload)

    assert response.status_code == 422


def test_create_document_with_invalid_field_type():
    payload = {
        "filename": 123,
        "file_path": "data/document.pdf"
    }

    response = client.post("/documents/", json=payload)

    assert response.status_code == 422