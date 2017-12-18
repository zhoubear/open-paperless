'use strict';

waitForJQuery(function() {
    jQuery(document).ready(function() {
        $('.metadata-value').on('input', function(event) {
            // Check the checkbox next to a metadata value input when there is
            // data entry in the value's input.
            $(event.target).parents('tr').find(':checkbox').prop('checked', true);
        });
    });
});
