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
            if (input.type === "file") {
                return; // Skip file input
            }
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




// submit form
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('eventForm');
    form.addEventListener('submit', async function(event) {
        event.preventDefault();
        const formData = new FormData(form);
        console.log('Form Data:', Array.from(formData.entries())); // Log form data to check if 'name' is included

        const eventId = form.dataset.eventId;
        const url = eventId ? `/host/manage_event/${eventId}/` : '/host/';
        const method = 'POST'; // Always use POST

        const response = await fetch(url, {
            method: method,
            body: formData, // Send FormData directly
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });

        const result = await response.json();
        console.log(result.id)
        
        if (result.success) {
            document.querySelector('.modal-content').innerHTML = `
                <div class="event-details">
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    <h2 class="modal-title">${result.name}</h2>
                    <img src="${result.poster}" alt="Event Poster" class="img-fluid">
                    <p><strong>Description:</strong> ${result.description}</p>
                    <p><strong>Location:</strong> ${result.location}</p>
                    <p><strong>Start Time:</strong> ${new Date(result.start_time).toLocaleString()}</p>
                    <p><strong>End Time:</strong> ${new Date(result.end_time).toLocaleString()}</p>
                    <button class="btn btn-primary manage-event" data-event-id="${result.id}">Manage Event</button>
                </div>
            `;
        } else {
            console.log(result.errors);
        }
    });
       
    // Event delegation for dynamically created "Manage Event" button
    document.querySelector('.modal-content').addEventListener('click', function (event) {
        if (event.target.classList.contains('manage-event')) {
            const eventId = event.target.getAttribute('data-event-id');
            window.location.href = `/host/manage_event/${eventId}`;
        }
    });
});







document.addEventListener('DOMContentLoaded', () => {
    fetch('/host/api/events')
        .then(response => response.json())
        .then(events => {
            console.log(events); // Log the response to the console
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
                        <p class="card-text"><small class="text-muted">${new Date(event.start_time).toLocaleString()}</small></p>
                        <button class="btn btn-primary manage-event" data-event-id="${event.id}">Manage Event</button>
                    </div>
                </div>
            </div>
        `;
        container.innerHTML += eventCard;
    });
    // Reattach event listeners to the new buttons
    document.querySelectorAll('.manage-event').forEach(button => {
        button.addEventListener('click', (event) => {
            const eventId = event.target.getAttribute('data-event-id');
            window.location.href = `/host/manage_event/${eventId}`;
        });
    });
}





function event_details(eventId = null) {
    const modal = new bootstrap.Modal(document.getElementById('eventModal'));
    const form = document.getElementById('eventForm');

    if (eventId) {
        form.dataset.eventId = eventId; // Set event ID for updating
        fetch(`/host/manage_event/${eventId}/`, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                // Populate form fields with fetched data
                const preview = document.getElementById('preview');
                    if (preview) {
                        preview.src = data.poster;
                        preview.style.display = 'block'; // Make sure the image is visible
                    } else {
                        console.error('Element with ID preview not found');
                    }
                document.getElementById('eventName').value = data.name;
                document.getElementById('eventCategory').value = data.category;
                document.getElementById('eventStartTime').value = data.start_time.slice(0, -1);
                document.getElementById('eventEndTime').value = data.end_time.slice(0, -1);
                document.getElementById('eventDescription').value = data.description;
                document.getElementById('eventLocation').value = data.location;
                document.getElementById('undisclosedAddress').value = data.undisclosed;
                document.getElementById('directions').value = data.directions;
                document.getElementById('socials').value = data.socials;
                
                document.getElementById('eventForm').dataset.eventId = eventId;
                document.getElementById('eventModalLabel').innerText = 'Edit Event';
                document.getElementById('saveButton').innerText = 'Update Event';
                document.getElementById('saveButton').disabled = false; // Enable the button
            })
            .catch(error => console.error('Error fetching event details:', error));
    } else {
        form.dataset.eventId = ''; // Clear event ID for new events
        form.reset();
    }
    modal.show();
}



// ticket creation
document.addEventListener('DOMContentLoaded', (event) => {
    document.getElementById('ticketForm').addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent the default form submission
        const form = document.getElementById('ticketForm');
        const formData = new FormData(form);
        const eventId = form.dataset.eventId;
        const url = `/host/manage_event/${eventId}/tickets/`;
        fetch(url, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': formData.get('csrfmiddlewaretoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById('ticketForm').style.display = 'none';
                document.getElementById('ticketCard').style.display = 'block';
                document.getElementById('ticketCard').innerHTML = `
                    <h2>Eventid: ${data.event_id}</h2>
                    <h2>Type: ${data.type}</h2>
                    <p>Price: ${data.price}</p>
                    <p>Quantity: ${data.quantity}</p>
                    <p>Description: ${data.description}</p>
                    <p>Deadline: ${data.deadline}</p>
                    <button class="btn btn-secondary" id="addTicketBtn">Add Ticket</button>
                    <button class="btn btn-success" id="doneBtn">Done</button>
                `;

                document.getElementById('addTicketBtn').addEventListener('click', function() {
                    document.getElementById('ticketForm').reset();
                    document.getElementById('ticketForm').style.display = 'block';
                    document.getElementById('ticketCard').style.display = 'none';
                });
            
                document.getElementById('doneBtn').addEventListener('click', function() {
                    $('#ticketModal').modal('hide');
                    const tableBody = document.querySelector('table tbody');
                    const newRow = document.createElement('tr');
                    newRow.innerHTML = `
                        <td>${data.type}</td>
                        <td>${data.price}</td>
                        <td>${data.quantity}</td>
                        <td>${data.description}</td>
                        <td>${data.deadline}</td>
                    `;
                    tableBody.appendChild(newRow);
                    location.reload();
                });
            } else {
                console.log("Form errors:", data.errors);
            }
        });  
    });
});

// for free ticket
document.addEventListener('DOMContentLoaded', (event) => {
    const priceInput = document.getElementById('price');
    const freeCheckbox = document.getElementById('freeCheckbox');
    const hiddenPrice = document.getElementById('hiddenPrice');

    freeCheckbox.addEventListener('change', function() {
        if (this.checked) {
            priceInput.value = "";
            priceInput.disabled = true;
            hiddenPrice.value = 0;
        } else {
            priceInput.disabled = false;
            hiddenPrice.value = priceInput.value;
        }
    });

    priceInput.addEventListener('input', function() {
        hiddenPrice.value = priceInput.value;
    });
});