
'use strict';
document.addEventListener('DOMContentLoaded', function () {
    var statusElement = document.getElementById('status');
    var cancelReasonContainer = document.getElementById('cancel_reason_container');
    var rejectReasonContainer = document.getElementById('reject_reason_container');

    function toggleReasonContainers() {
        var status = statusElement.value;
        if (status === 'Cancelled') {
            cancelReasonContainer.style.display = 'block';
            rejectReasonContainer.style.display = 'none';
        } else if (status === 'Rejected') {
            rejectReasonContainer.style.display = 'block';
            cancelReasonContainer.style.display = 'none';
        } else {
            cancelReasonContainer.style.display = 'none';
            rejectReasonContainer.style.display = 'none';
        }
    }

    statusElement.addEventListener('change', toggleReasonContainers);

    // Initial check in case the page is loaded with a status already set
    toggleReasonContainers();
});
