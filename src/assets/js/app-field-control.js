
'use strict';

 document.getElementById('status').addEventListener('change', function() {
        var status = this.value;
        var cancelReasonContainer = document.getElementById('cancel_reason_container');
        var rejectReasonContainer = document.getElementById('reject_reason_container');

        if (status === 'cancelled') {
            cancelReasonContainer.style.display = 'block';
            rejectReasonContainer.style.display = 'none';
        } else if (status === 'rejected') {
            rejectReasonContainer.style.display = 'block';
            cancelReasonContainer.style.display = 'none';
        } else {
            cancelReasonContainer.style.display = 'none';
            rejectReasonContainer.style.display = 'none';
        }
    });
