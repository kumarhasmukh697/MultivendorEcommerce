// ...existing code...
    // <script src="https://maps.googleapis.com/maps/api/js?key=YOUR_GOOGLE_API_KEY&libraries=places"></script>
    // <script>
        function initAutoComplete(){
            var autocomplete;
            var id = 'id_address' // ID of your address input field
            
            autocomplete = new google.maps.places.Autocomplete(
                document.getElementById(id),
                {
                    types: ['geocode', 'establishment'],
                    //default in this app is "IN" - add your country code
                    componentRestrictions: {'country': ['in']},
                }
            );

            autocomplete.addListener('place_changed', function() {
                var place = autocomplete.getPlace();
                
                // Get address components
                for(var i=0; i<place.address_components.length; i++){
                    for(var j=0; j<place.address_components[i].types.length; j++){
                        // Get street number
                        if(place.address_components[i].types[j] == "street_number"){
                            var street_number = place.address_components[i].long_name;
                        }
                        // Get route (street)
                        if(place.address_components[i].types[j] == "route"){
                            var route = place.address_components[i].long_name;
                        }
                        // Get city
                        if(place.address_components[i].types[j] == "locality"){
                            document.getElementById('id_city').value = place.address_components[i].long_name;
                        }
                        // Get state
                        if(place.address_components[i].types[j] == "administrative_area_level_1"){
                            document.getElementById('id_state').value = place.address_components[i].long_name;
                        }
                        // Get country
                        if(place.address_components[i].types[j] == "country"){
                            document.getElementById('id_country').value = place.address_components[i].long_name;
                        }
                        // Get postal code
                        if(place.address_components[i].types[j] == "postal_code"){
                            document.getElementById('id_pin_code').value = place.address_components[i].long_name;
                        }
                    }
                }

                // Get latitude and longitude
                document.getElementById('id_latitude').value = place.geometry.location.lat();
                document.getElementById('id_longitude').value = place.geometry.location.lng();
            });
        }
    // </script>
    // <script>
        google.maps.event.addDomListener(window, 'load', initAutoComplete);
    // </script>
// {% endblock %}