// to get event modal prefilled for editing or empty for creating
function event_details(eventId = null) {
    const modal = new bootstrap.Modal(document.getElementById('eventModal'));
    const form = document.getElementById('eventForm');
  
    if (eventId) {
      // Fetch event data from the server
      fetch(`/get_event/${eventId}/`)
        .then(response => response.json())
        .then(data => {
          // Populate form fields with data
          form.elements['poster'].value = ""; // File input can't be prefilled
          form.elements['name'].value = data.name;
          form.elements['category'].value = data.category;
          form.elements['start_time'].value = data.start_time;
          form.elements['end_time'].value = data.end_time;
          form.elements['description'].value = data.description;
          form.elements['undisclosed'].checked = data.undisclosed;
          form.elements['location'].value = data.location;
          form.elements['directions'].value = data.directions;
          form.elements['socials'].value = data.socials;
        });
    } else {
      // Clear form for a new event
      form.reset();
    }
  
    modal.show();
}


function getCookie(name) {
    const cookieValue = document.cookie
        .split('; ')
        .find(row => row.startsWith(name))
        ?.split('=')[1];
    return decodeURIComponent(cookieValue);
}




// ensure form is filled before user can save
document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById("eventForm");
    const saveButton = document.getElementById("saveButton");

    form.addEventListener("input", function() {
        let allFilled = true;
        form.querySelectorAll("input, textarea, select").forEach(function(input) {
            if (!input.value) {
                allFilled = false;
            }
        });
        saveButton.disabled = !allFilled;
    });
});


// to preview image in event details form
document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('eventPoster');
    const preview = document.getElementById('preview');

    input.addEventListener('change', () => {
        if (input.files && input.files[0]) {
            const reader = new FileReader();

            reader.onload = function (e) {
                preview.src = e.target.result; // Set image source
                preview.style.display = 'block'; // Display the image
            };

            reader.readAsDataURL(input.files[0]); // Read file as DataURL
        } else {
            console.error("No file selected or unsupported file type.");
        }
    });
});


// for submitting the event details
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('eventForm');
    form.addEventListener('submit', async function(event) {
        event.preventDefault(); // Prevent the default form submission

        const formData = new FormData(form);
        const response = await fetch(form.action, {
            method: 'POST',
            body: formData,
        });

        const result = await response.json();
        if (result.success) {
            // Update the modal with event details
            document.querySelector('.modal-content').innerHTML = `
                <div class="event-details">
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    <h2 class="modal-title">${result.name}</h2>
                    <p><strong>Category:</strong> ${result.category}</p>
                    <img src="${result.poster}" alt="Event Poster" class="img-fluid">
                    <p><strong>Description:</strong> ${result.description}</p>
                    <p><strong>Location:</strong> ${result.location}</p>
                    <p><strong>Start Time:</strong> ${result.start_time}</p>
                    <p><strong>End Time:</strong> ${result.end_time}</p>
                    <button class="btn btn-primary">Manage Event</button>
                </div>
            `;
        } else {
            // Handle errors
            console.log(result.errors);
        }
    });
});




document.addEventListener('DOMContentLoaded', () => {
    fetch('/api/events')
        .then(response => response.json())
        .then(events => {
            displayEvents(events);
        });
});


function displayEvents(events) {
    const container = document.querySelector('#events-container');
    container.innerHTML = ''; // Clear the container first
    events.forEach(event => {
        const eventCard = `
            <div class="col-md-4">
                <div class="card">
                    <div class="card-body">
                        <img src="${event.poster}" alt="Event Poster" class="img-fluid">
                        <h5 class="card-title">${event.name}</h5>
                        <p class="card-text">${event.description}</p>
                        <p class="card-text"><small class="text-muted">${event.start_time}</small></p>
                        <button class="btn btn-primary">Manage Event</button>
                    </div>
                </div>
            </div>
        `;
        container.innerHTML += eventCard;
    });
}
