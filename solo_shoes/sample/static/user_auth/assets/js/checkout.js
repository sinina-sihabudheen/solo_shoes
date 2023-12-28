$(document).ready(function (){
    $('.payWithrazorpay').click(function (e){
        e.preventDefault();
        console.log("EXECUTED")

         // Fetch values from form elements using name attributes
        var selectedAddressId = $('input[name="shipping_address"]:checked').val();
        

        // Fetch values from data attributes
        var full_name = $(this).data('full_name');
        var phone = $(this).data('phone');

        
        
        $.ajax({
            method: "GET",
            url: "/carts/proceed_to_pay/",
            success: function (response){
              console.log(response)
              console.log("Ajax response:", response);


              var options = {
            "key": "rzp_test_jqDk0ijEJwoHUe", // Enter the Key ID generated from the Dashboard
            "amount": response.total_price * 100,  // Amount is in currency subunits. Default currency is INR. Hence, 50000 refers to 50000 paise
            "currency": "INR",
            "name": "SOLO SHOES", //your business name
            "description": "Thank you for buying from us...",
            "image": "https://example.com/your_logo",
       
            "handler": function (responseb){
                alert(responseb.razorpay_payment_id);
               data = {
                'selectedAddressId':selectedAddressId,
                'pay_mod':'RAZ',
                // 'transaction_id': responseb.razorpay_payment_id,
               
                csrfmiddlewaretoken:token,
               }
               $.ajax({
                    method : "POST",
                    url: "/carts/place_order_raz/",
                    data: data,
                    success: function(responsec) {
                        console.log("Response Object:", responsec);
                        Swal.fire("Congrats!!!", responsec.message, "success").then((value) => {
                            // window.location.href = '/carts//';
                        });
                    }
               });
            },
            "prefill": { //We recommend using the prefill parameter to auto-fill customer's contact information, especially their phone number
                "full_name": full_name, //your customer's name
                "phone": phone,  //Provide the customer's phone number for better conversion rates 
            },
            "theme": {
                "color": "#3399cc"
            }
        };
        var rzp1 = new Razorpay(options);     
        rzp1.open();
            }
        })

        
    });
});


