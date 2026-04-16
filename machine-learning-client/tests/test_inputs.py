from inputs import CMInputs


def test_cminputs_defaults():
    data = CMInputs()
    assert data.session_id is None
    assert data.intended_university is None
    assert data.user_essay is None
    assert data.result is None


def test_cminputs_accepts_values():
    data = CMInputs(
        session_id="123",
        intended_university="NYU",
        user_essay="My essay",
        user_interview_response="My response",
        essay_file_name="essay.pdf",
        notes="Strong extracurriculars",
        sat_score=1500,
        gpa=4,
        essay_pdf_bytes=b"abc",
        result="Done",
    )

    assert data.session_id == "123"
    assert data.intended_university == "NYU"
    assert data.sat_score == 1500
    assert data.gpa == 4
    assert data.essay_pdf_bytes == b"abc"
    assert data.result == "Done"