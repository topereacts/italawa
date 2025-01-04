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



document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('openModal').onclick = function() {
      const eventId = document.getElementById('eventDetail').getAttribute('data-event-id');
      fetch(`/event_detail/${eventId}/get_tickets/`)
        .then(response => response.json())
        .then(data => {
          const ticketContainer = document.getElementById('ticketContainer');
          ticketContainer.innerHTML = ''; // Clear previous content
          data.tickets.forEach(ticket => {
            const ticketCard = document.createElement('div');
            ticketCard.className = 'card mb-3';
            console.log(ticket.id)
            ticketCard.innerHTML = `
                <div class="card-body">
                    <h5 class="card-title">${ticket.type}</h5>
                    <p class="card-text">${ticket.description}</p>
                    <p class="card-text">Price: ₦${ticket.price}</p>
                    <p class="card-text">Available: ${ticket.quantity}</p>
                    <input type="hidden" class="ticket_id" value="${ticket.id}">
                    <select class="quantity-select" data-id="${ticket.id}" data-price="${ticket.price}">
                        ${Array.from({ length: ticket.quantity + 1 }, (_, i) => `<option value="${i}">${i}</option>`).join('')}
                    </select>
                </div>
            `;
            ticketContainer.appendChild(ticketCard);
          });
          $('#ticketModal').modal('show');
        });
    };
});


document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('ticketContainer').addEventListener('change', function(event) {
        console.log("Event listener triggered");
        if (event.target.classList.contains('quantity-select')) {
        let subtotal = 0;
        document.querySelectorAll('.quantity-select').forEach(select => {
            const quantity = parseInt(select.value);
            const price = parseFloat(select.getAttribute('data-price'));
            subtotal += quantity * price;
        });
        const tax = subtotal * 0.1; // Assuming 10% tax
        const total = subtotal + tax;
        document.getElementById('subtotal').innerText = subtotal.toFixed(2);
        document.getElementById('tax').innerText = tax.toFixed(2);
        document.getElementById('total').innerText = total.toFixed(2);
        }
    });
});




// document.addEventListener('DOMContentLoaded', function() {
//     const paymentForm = document.getElementById('paymentForm');
//     paymentForm.addEventListener("submit", payWithPaystack, false);

//     function payWithPaystack(e) {
//         e.preventDefault();

//         const eventId = document.getElementById('eventDetail')?.getAttribute('data-event-id');
//         if (!eventId) {
//             console.error('Event ID is missing.');
//             return;
//         }

//         const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
//         if (!csrftoken) {
//             console.error('CSRF token is missing.');
//             return;
//         }

//         const handler = PaystackPop.setup({
//             key: 'pk_test_553d9f0f523ae22fcbb9131cc4b4f2fcce2d3c69',
//             email: document.getElementById("email").value,
//             amount: document.getElementById("total").innerText * 100,
//             currency: 'NGN',
//             ref: '' + Math.floor((Math.random() * 1000000000) + 1),
//             onClose: function() {
//                 alert('Window closed.');
//             },
//             callback: function(response) {
//                 console.log('Payment complete! Reference:', response.reference);

//                 const orderDetails = {
//                     ticket_id: document.getElementById("ticket_id")?.value,
//                     full_name: document.getElementById("fullName")?.value,
//                     email: document.getElementById("email")?.value,
//                     phone: document.getElementById("phone")?.value,
//                     reference: response.reference
//                 };

//                 console.log('Order Details:', orderDetails);

//                 fetch(`/event_detail/${eventId}/save_order/`, {
//                     method: 'POST',
//                     headers: {
//                         'Content-Type': 'application/json',
//                         'X-CSRFToken': csrftoken
//                     },
//                     body: JSON.stringify(orderDetails)
//                 })
//                 .then(response => {
//                     console.log('Fetch response received, status:', response.status);
//                     if (!response.ok) {
//                         throw new Error(`HTTP error! status: ${response.status}`);
//                     }
//                     return response.json();
//                 })
//                 .then(data => {
//                     console.log('Order saved:', data);
                
//                     let ticketDetails = '';
//                     data.tickets.forEach(ticket => {
//                         ticketDetails += `
//                             <p>${ticket.type} Ticket</p>
//                             <p>${ticket.description}</p>
//                             <p>Order ID: ${ticket.unique_order_id}</p>
//                             <p>Price: NGN ${ticket.price.toFixed(2)}</p>
//                             <img src="${ticket.barcode_url}" alt="Barcode for ${ticket.type} Ticket" />
//                         `;
//                     });
                
//                     document.getElementById("paymentForm").innerHTML = `
//                         <p>Full Name: ${data.full_name}</p>
//                         <p>Email: ${data.email}</p>
//                         <p>Phone: ${data.phone}</p>
//                         ${ticketDetails}
//                         <p>Total Amount Paid: NGN ${data.total_amount.toFixed(2)}</p>
//                     `;
//                 })               
//                 .catch(error => console.error('Error:', error));
//             }
//         });
//         handler.openIframe();
//     }
// });

document.addEventListener('DOMContentLoaded', function() {
    const paymentForm = document.getElementById('paymentForm');
    paymentForm.addEventListener("submit", payWithPaystack, false);

    function payWithPaystack(e) {
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
    
        const totalAmount = document.getElementById("total").innerText * 100; // Amount in kobo for Paystack
        const email = document.getElementById("email").value;
    
        const handler = PaystackPop.setup({
            key: 'pk_test_553d9f0f523ae22fcbb9131cc4b4f2fcce2d3c69',
            email: email,
            amount: totalAmount,
            currency: 'NGN',
            ref: '' + Math.floor((Math.random() * 1000000000) + 1),
            onClose: function() {
                alert('Window closed.');
            },
            callback: function(response) {
                console.log('Payment complete! Reference:', response.reference);
    
                const orderDetails = {
                    full_name: document.getElementById("fullName").value,
                    email: email,
                    phone: document.getElementById("phone").value,
                    tickets: selectedTickets,
                    reference: response.reference
                };

                console.log('Order Details:', orderDetails);
                fetch(`/event_detail/${eventId}/save_order/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrftoken
                    },
                    body: JSON.stringify(orderDetails)
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
                        <p>Total Amount Paid: ₦${data.total_amount} minus %tax</p>
                    `;
                })
                .catch(error => console.error('Error:', error));
            }
        }); 
        handler.openIframe();
    }    
});


function setDateFilter(filter, button) {
    const buttons = document.querySelectorAll('.btn-outline-primary');
    buttons.forEach(btn => btn.classList.remove('active'));
    button.classList.add('active');
    const today = new Date().toISOString().split('T')[0];
    let startDate, endDate;

    if (filter === 'today') {
        startDate = endDate = today;
    } else if (filter === 'tomorrow') {
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        startDate = endDate = tomorrow.toISOString().split('T')[0];
    } else if (filter === 'weekend') {
        const date = new Date();
        const day = date.getDay();
        const diffToSaturday = 6 - day;
        const diffToSunday = 7 - day;
        const saturday = new Date(date.setDate(date.getDate() + diffToSaturday)).toISOString().split('T')[0];
        const sunday = new Date(date.setDate(date.getDate() + diffToSunday)).toISOString().split('T')[0];
        startDate = saturday;
        endDate = sunday;
    }

    document.getElementById('startDate').value = startDate;
    document.getElementById('endDate').value = endDate;
}


function updatePrice(value) {
    document.getElementById('priceValue').innerText = value;
}
