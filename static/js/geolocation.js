
function getLocation(event) {
    event.preventDefault(); // Prevent form from submitting immediately
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            // Set the hidden fields
            document.getElementById('latitude').value = position.coords.latitude;
            document.getElementById('longitude').value = position.coords.longitude;
            console.log(position.coords.latitude, position.coords.longitude);
            // Submit the form after setting location
            event.target.form.submit();
        }, function() {
            alert("Sorry, no position available.");
            event.target.form.submit(); // Submit anyway if denied
        });
    } else {
        alert("Geolocation is not supported by this browser.");
        event.target.form.submit();
    }
}

// Attach the handler to the search button
document.addEventListener('DOMContentLoaded', function() {
    var searchBtn = document.querySelector('input[type="submit"][value="Search"]');
    if (searchBtn) {
        searchBtn.addEventListener('click', getLocation);
    }
});