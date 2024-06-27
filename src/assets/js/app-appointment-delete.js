'use strict';

document.addEventListener('DOMContentLoaded', function (e) {
  (function () {
    const deleteButtons = document.querySelectorAll('.delete_appointment');
    deleteButtons.forEach(deleteButton => {
      deleteButton.addEventListener('click', function (e) {
        const patient = this.getAttribute('data-appointment-patient');
        Swal.fire({
          title: 'Delete Appointment?',
          html: `<p class="text-danger">Are you sure you want to delete appointment of ?<br> <span class="fw-medium text-body">${patient}</span></p>`,
          icon: 'warning',
          showCancelButton: true,
          confirmButtonText: 'Delete',
          cancelButtonText: 'Cancel',
          customClass: {
            confirmButton: 'btn btn-primary waves-effect waves-light',
            cancelButton: 'btn btn-secondary waves-effect waves-light'
          }
        }).then(result => {
          if (result.isConfirmed) {
            window.location.href = this.getAttribute('href'); //redirect to herf
          } else {
            Swal.fire({
              title: 'Cancelled',
              html: `<p>Did not delete <span class="fw-medium text-primary">${userName}</span> Transaction!</p>`,
              icon: 'error',
              confirmButtonText: 'Ok',
              customClass: {
                confirmButton: 'btn btn-success waves-effect waves-light'
              }
            });
          }
        });
      });
    });
  })();
});
