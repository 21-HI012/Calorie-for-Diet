function readImage(input) {
  if (input.files && input.files[0]) {
    const reader = new FileReader();
    reader.onload = function (e) {
      const previewImage = document.getElementById("preview-image");
      previewImage.src = e.target.result;
    };
    reader.readAsDataURL(input.files[0]);
  }
}

document.getElementById("input-image").addEventListener("change", function () {
  readImage(this);
});
