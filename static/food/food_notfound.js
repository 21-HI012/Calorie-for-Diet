$(document).ready(function () {
  var maxFields = 5; // Maximum number of input fields
  var addButton = $(".add_food_button"); // Add button selector
  var wrapper = $(".input_fields_wrap"); // Container for input fields
  var fieldHTML =
    '<div class="input-block"><input type="text" name="food_names[]" placeholder="음식명" class="food-input" /><a href="#" class="remove_field">✖</a></div>'; // New input field html

  var x = 1; // Initial field count
  $(addButton).click(function (e) {
    e.preventDefault();
    if (x < maxFields) {
      // Check the maximum limit of input fields
      x++; // Increment field counter
      $(wrapper).append(fieldHTML); // Add new input field html
    }
  });

  $(wrapper).on("click", ".remove_field", function (e) {
    e.preventDefault();
    $(this).parent(".input-block").remove(); // Remove the parent of the remove button
    x--; // Decrement field counter
  });
});
