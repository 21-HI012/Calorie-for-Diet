document.addEventListener("DOMContentLoaded", function () {
  // Flash 메시지가 포함된 요소를 선택합니다.
  const messageAlerts = document.querySelectorAll(".message-alert");

  // 각 메시지 요소에 대해 클릭 이벤트를 추가합니다.
  messageAlerts.forEach(function (message) {
    // 메시지를 클릭하면 해당 메시지가 사라지도록 처리합니다.
    message.addEventListener("click", function () {
      message.style.display = "none";
    });
  });
});
