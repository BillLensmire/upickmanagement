(function($) {
    'use strict';
    $(function() {
        console.log('Planting schedule JS loaded');
        
        const plantField = $('#id_plant');
        const insidePlantingField = $('#id_inside_planting_date').closest('.form-row');
        const outsidePlantingField = $('#id_outside_planting_date').closest('.form-row');
        
        function updatePlantingFields() {
            console.log('updatePlantingFields called');
            // Get the selected plant's data
            const plantId = plantField.val();
            console.log('Plant ID:', plantId);
            if (!plantId) {
                return;
            }
            
            // Show/hide planting date fields based on planting method
            $.get(`/admin/plants/plant/${plantId}/`, function(data) {
                const plantingMethod = $(data).find('#id_planting_method').val();
                
                console.log('Planting method:', plantingMethod);
                
                if (plantingMethod === 'TRANSPLANT') {
                    insidePlantingField.show();
                    outsidePlantingField.show();
                } else if (plantingMethod === 'DIRECT') {
                    insidePlantingField.hide();
                    outsidePlantingField.show();
                } else {  // BOTH
                    insidePlantingField.show();
                    outsidePlantingField.show();
                }
            });
        }
        
        // Initial update
        updatePlantingFields();

        // Function to update planting dates based on harvest date
        function updatePlantingDates() {
            console.log('updatePlantingDates called');
            var harvestDate = $('#id_harvest_date').val();
            var plantId = $('#id_plant').val();
            
            console.log('Harvest date:', harvestDate);
            console.log('Plant ID:', plantId);
            
            if (harvestDate && plantId) {
                console.log('Making AJAX call');
                // Get the current URL path
                var currentPath = window.location.pathname;
                console.log('Current path:', currentPath);
                
                // Construct the calculate URL by replacing the last part of the path
                var calculateUrl;
                if (currentPath.includes('/add/')) {
                    calculateUrl = 'calculate-dates';
                } else {
                    // For change form, strip off 'change/' and add 'calculate-dates/'
                    calculateUrl = currentPath.replace(/change\/$/, 'calculate-dates');
                }
                
                console.log('Calculate URL:', calculateUrl);
                
                $.ajax({
                    url: calculateUrl,
                    data: {
                        'harvest_date': harvestDate,
                        'plant_id': plantId
                    },
                    dataType: 'json',
                    success: function(data) {
                        console.log('AJAX success:', data);
                        if (data.success) {
                            $('#id_inside_planting_date').val(data.inside_date || '');
                            $('#id_outside_planting_date').val(data.outside_date || '');
                            $('#id_expected_harvest_start').val(data.harvest_date || '');
                            if (data.outside_flag === 'yes') {
                                const helpText = document.getElementById('id_outside_planting_date_helptext');
                                helpText.textContent = 'WARNING: OUTSIDE PLANTING DATE IS PRIOR TO FIRST FROST DATE';
                                helpText.style.color = 'red'; // Optional: Add styling
                            }
                            else {
                                const helpText = document.getElementById('id_outside_planting_date_helptext');
                                helpText.textContent = 'Date when the seed/plant will be planted outside the garden';
                                helpText.style.color = 'black'; // Optional: Add styling
                            }
                        }
                    },
                    error: function(xhr, status, error) {
                        console.error('AJAX error:', status, error);
                        console.error('Response:', xhr.responseText);
                        console.error('URL attempted:', calculateUrl);
                    }
                });
            }
        }

        // Update dates when harvest date changes
        $('#id_harvest_date').on('change', function() {
            console.log('Harvest date changed');
            updatePlantingDates();
        });
        
        // Add event listener for harvest date field blur
        $('#id_harvest_date').on('blur', function() {
            const harvestDate = $(this).val();
            if (harvestDate) {
                // Get the plant ID from the plant select field
                const plantId = $('#id_plant').val();
                if (plantId) {
                    // Make AJAX call to calculate dates
                    $.ajax({
                        url: 'calculate-dates/',
                        data: {
                            'plant_id': plantId,
                            'harvest_date': harvestDate
                        },
                        dataType: 'json',
                        success: function(data) {
                            if (data.success) {
                                $('#id_inside_planting_date').val(data.inside_date || '');
                                $('#id_outside_planting_date').val(data.outside_date || '');
                                if (data.outside_flag === 'yes') {
                                    const helpText = document.getElementById('id_outside_planting_date_helptext');
                                    helpText.textContent = 'WARNING: OUTSIDE PLANTING DATE IS PRIOR TO FIRST FROST DATE';
                                    helpText.style.color = 'red';
                                }
                                else {
                                    const helpText = document.getElementById('id_outside_planting_date_helptext');
                                    helpText.textContent = 'Date when the seed/plant will be planted outside the garden';
                                    helpText.style.color = 'black';
                                }
                            }
                        }
                    });
                }
            }
        });

        // Also update when plant selection changes
        $('#id_plant').on('change', function() {
            console.log('Plant changed');
            if ($('#id_harvest_date').val()) {
                updatePlantingDates();
            }
            updatePlantingFields();
        });

        console.log('Event handlers attached');
    });
})(django.jQuery);