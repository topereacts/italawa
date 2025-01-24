# Django Event/Ticketing App

## An Event and ticketing project using Django apps

This project provides a streamlined platform for managing events and ticketing. Users can browse events, purchase tickets using **Paystack** integration, and create their own events after registering. The app is divided into two main modules:

- **Events App**: Public-facing section where users can explore events and purchase tickets.
- **Host App**: Backend for event organizers to manage their events, tickets, and staff.

## How to install this Django event ticketing app
1. Clone this project
    Set up a virtual environment:
2. python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
3. Install dependencies:
    pip install -r requirements.txt
4. Set up the database:
    python manage.py migrate
5. Configure environment variables:
    Create a .env file in the project root.
    Add required configurations, including your Paystack API keys:
    PAYSTACK_PUBLIC_KEY=your-paystack-public-key
    PAYSTACK_SECRET_KEY=your-paystack-secret-key

## Distinctiveness and Complexity

### Why this project satisfies the distinctiveness and complexity requirements:

1. **Distinctiveness**:
   - This project is distinct from basic Django projects like blogs or to-do apps because it integrates multi-user functionality, real-time ticket validation, and staff role management.
   - It includes a clear separation of responsibilities between the **Events App** (for users) and the **Host App** (for event organizers).
   - The integration of Paystack for payment processing adds a layer of real-world application not found in simpler projects.

2. **Complexity**:
   - The app features multiple user roles (users, event organizers, and staff) with specific access permissions.
   - Dynamic dashboard functionalities provide event organizers with real-time insights into ticket sales and revenue.
   - Scanning tickets using a barcode scanner and validating them against the database in real time adds technical complexity.
   - Staff management functionality restricts staff access to only specific parts of the app, ensuring secure and efficient operations during events.

---

## Features

### Events App
- Explore upcoming events with detailed descriptions.
- Purchase tickets securely via Paystack.
#### Paystack Integration

The following JavaScript snippet is used to handle the Paystack payment process:
```javascript
document.addEventListener('DOMContentLoaded', function () {
    const paymentForm = document.getElementById('paymentForm');
    paymentForm.addEventListener("submit", payWithPaystack, false);

    function payWithPaystack(e) {
        document.getElementById("checkoutButton").innerHTML = '<i class="bi bi-arrow-clockwise"></i> Processing...';
        e.preventDefault();

        const eventId = document.getElementById('eventDetail')?.getAttribute('data-event-id');
        if (!eventId) {
            console.error('Event ID is missing.');
            return;
        }

        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        if (!csrftoken) {
            console.error('CSRF token is missing.');
            return;
        }

        const selectedTickets = [];
        document.querySelectorAll('.quantity-select').forEach(select => {
            const quantity = parseInt(select.value, 10);
            if (quantity > 0) {
                selectedTickets.push({
                    ticket_id: select.getAttribute('data-id'),
                    price: parseFloat(select.getAttribute('data-price')),
                    quantity: quantity
                });
            }
        });

        if (selectedTickets.length === 0) {
            alert('Please select at least one ticket.');
            return;
        }

        const totalAmount = parseFloat(document.getElementById("total").innerText) * 100; // Amount in kobo
        const email = document.getElementById("email").value;

        if (totalAmount === 0) {
            // If total amount is 0, post directly without Paystack
            const orderDetails = {
                full_name: document.getElementById("fullName").value,
                email: email,
                phone: document.getElementById("phone").value,
                tickets: selectedTickets,
                reference: 'FREE_ORDER_' + Math.floor((Math.random() * 1000000000) + 1),
            };

            fetch(`/event_detail/${eventId}/save_order/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken,
                },
                body: JSON.stringify(orderDetails),
            })
                .then(response => response.json())
                .then(data => {
                    console.log('Order saved:', data);

                    let ticketDetails = '';
                    data.tickets.forEach(ticket => {
                        ticketDetails += `
                            <p>${ticket.type} Ticket</p>
                            <p>${ticket.description}</p>
                            <p>Order ID: ${ticket.unique_order_id}</p>
                            <p>Price: ₦${ticket.price}</p>
                            <img src="${ticket.barcode_url}" alt="Barcode for ${ticket.type} Ticket" />
                        `;
                    });

                    document.getElementById("paymentForm").innerHTML = `
                        <p>Full Name: ${data.full_name}</p>
                        <p>Email: ${data.email}</p>
                        <p>Phone: ${data.phone}</p>
                        ${ticketDetails}
                        <p>Total Amount Paid: ₦${data.total_amount}</p>
                    `;
                })
                .catch(error => console.error('Error:', error));

            return; // Exit the function, bypassing Paystack
        }

        const handler = PaystackPop.setup({
            key: 'ADD PUBLIC KEY HERE',
            email: email,
            amount: totalAmount,
            currency: 'NGN',
            ref: '' + Math.floor((Math.random() * 1000000000) + 1),
            onClose: function () {
                alert('Window closed.');
            },
            callback: function (response) {
                console.log('Payment complete! Reference:', response.reference);

                const orderDetails = {
                    full_name: document.getElementById("fullName").value,
                    email: email,
                    phone: document.getElementById("phone").value,
                    tickets: selectedTickets,
                    reference: response.reference,
                };

                fetch(`/event_detail/${eventId}/save_order/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrftoken,
                    },
                    body: JSON.stringify(orderDetails),
                })
                    .then(response => response.json())
                    .then(data => {
                        console.log('Order saved:', data);

                        let ticketDetails = '';
                        data.tickets.forEach(ticket => {
                            ticketDetails += `
                                <p>${ticket.type} Ticket</p>
                                <p>${ticket.description}</p>
                                <p>Order ID: ${ticket.unique_order_id}</p>
                                <p>Price: ₦${ticket.price}</p>
                                <img src="${ticket.barcode_url}" alt="Barcode for ${ticket.type} Ticket" />
                            `;
                        });

                        document.getElementById("paymentForm").innerHTML = `
                            <p>Full Name: ${data.full_name}</p>
                            <p>Email: ${data.email}</p>
                            <p>Phone: ${data.phone}</p>
                            ${ticketDetails}
                            <p>Total Amount Paid: ₦${data.total_amount}</p>
                        `;
                    })
                    .catch(error => console.error('Error:', error));
            },
        });
        handler.openIframe();
    }
}); 
```


### Host App
- **Dashboard**: Overview of event details and ticket sales.
- **Ticket**: Create and manage tickets for events.
- **Scan Ticket**: Validate tickets in real-time during the event.
- **Revenue**: Monitor total revenue generated for each event.
- **Staff Management**: Add and manage staff with limited access for event day operations.

#### How i used QuaggaJS for real time scanning of Tickets

The following JavaScript snippet powers the real-time ticket scanning functionality using the `QuaggaJS` library:
```Javascript
document.addEventListener("DOMContentLoaded", function () {
    Quagga.init({
        inputStream: {
            name: "Live",
            type: "LiveStream",
            target: document.querySelector('#scanner-container')
        },
        decoder: {
            readers: ["code_128_reader"] // Adjust based on your barcode type
        }
    }, function (err) {
        if (err) {
            console.error(err);
            return;
        }
        Quagga.start();
    });

    const scannedTickets = new Set(); // Keep track of already scanned tickets

    Quagga.onDetected(function (result) {
        const ticketUniqueOrderId = result.codeResult.code;

        if (scannedTickets.has(ticketUniqueOrderId)) {
            alert("Ticket already scanned!");
            return;
        }

        fetch(`/host/check_in_ticket/?ticket_unique_order_id=${ticketUniqueOrderId}`)
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    updateTable(data.ticket_details);
                    scannedTickets.add(ticketUniqueOrderId); // Mark ticket as scanned
                } else {
                    alert(data.message || 'Check-in failed');
                }
            })
            .catch(error => console.error('Error:', error));
    });

    function updateTable(details) {
        const table = document.getElementById('ticket-table').getElementsByTagName('tbody')[0];
        const newRow = table.insertRow();

        newRow.insertCell(0).innerHTML = details.order_id;
        newRow.insertCell(1).innerHTML = details.ticket_unique_order_id;
        newRow.insertCell(2).innerHTML = details.checked_in_at;
        newRow.insertCell(3).innerHTML = details.ticket_type;
        newRow.insertCell(4).innerHTML = details.ticket_price;
        newRow.insertCell(5).innerHTML = details.ticket_description;
    }
});
```

---

## File Structure

### Key Files and Their Purposes:

- **events/views.py**: Handles logic for displaying events, purchasing tickets, and filtering events.
- **host/views.py**: Manages event creation, dashboards, ticket scanning, revenue tracking, and staff management.
- **events/models.py**: Defines the `User`, `Order` and `TicketInstance` models for storing event and ticket details.
- **host/models.py**: Includes models for managing events, staff, and Ticket functionalities.
- **templates/**:
  - **events/**: Contains templates for the public-facing event pages.
  - **host/**: Contains templates for the host dashboard, ticket management, and other management pages.
- **static/**: Includes CSS, JavaScript, and other front-end assets.
- **urls.py**: Defines URL routing for both the `events` and `host` apps.
- **settings.py**: Configures the Django project, including database, Paystack keys, and static files.


## Usage
### For Users:

* Browse the events on the homepage.
* Click on an event to view details and purchase tickets using Paystack.

### For Event Organizers:

* Register and log in to access the Host App.
* Create events and tickets via the dashboard.
* Use the "Manage Event" button to view dashboards, scan tickets, track revenue, and manage staff of specific events.

## Technologies Used

Backend: Django, Django ORM
Frontend: HTML, CSS, JavaScript, Bootstrap
Payment Gateway: Paystack
Database: PostgreSQL / SQLite
Real-Time Features: Barcode scanner integration for ticket validation

## Additional Information
* Staff Role: Staff accounts are limited to dashboard, ticket management, and ticket scanning functionalities for added security.
* Ticket Scanning: The barcode scanner ensures secure and efficient ticket validation during the event.
* Revenue Tracking: Real-time revenue statistics help organizers monitor their financial performance.
