function validateForm() {
  var fileInput = document.getElementById("input-image");
  if (!fileInput.files || fileInput.files.length === 0) {
    alert("이미지를 업로드해주세요.");
    return false; // Prevent form submission
  }
  return true; // Allow form submission
}
