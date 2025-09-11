document.querySelector("form").addEventListener("submit", function(event) {
  event.preventDefault(); // stops page refresh
  alert("Message sent!");
});
