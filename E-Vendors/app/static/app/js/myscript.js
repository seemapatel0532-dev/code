$('#slider1, #slider2, #slider3').owlCarousel({
    loop: true,
    margin: 20,
    responsiveClass: true,
    responsive: {
        0: {
            items: 2,
            nav: false,
            autoplay: true,
        },
        600: {
            items: 4,
            nav: true,
            autoplay: true,
        },
        1000: {
            items: 6,
            nav: true,
            loop: true,
            autoplay: true,
        }
    }
})

$('.plus-cart').click(function(){
    var id=$(this).attr("pid").toString();
    var eml=this.parentNode.children[2] 
    $.ajax({
        type:"GET",
        url:"/pluscart",
        data:{
            prod_id:id
        },
        success:function(data){
            eml.innerText=data.quantity 
            document.getElementById("amount").innerText=data.amount 
            document.getElementById("totalamount").innerText=data.totalamount
            window.location.href = "http://localhost:8000/cart/"
        }
    })
})

$('.minus-cart').click(function(){
    var id=$(this).attr("pid").toString();
    var eml=this.parentNode.children[2] 
    $.ajax({
        type:"GET",
        url:"/minuscart",
        data:{
            prod_id:id
        },
        success:function(data){
            eml.innerText=data.quantity 
            document.getElementById("amount").innerText= "₹"+data.amount
            document.getElementById("totalamount").innerText= "₹"+data.totalamount
            window.location.href = "http://localhost:8000/cart/"
        }
    })
})

// $(document).ready(function() {
//     // Get the CSRF token from the meta tag
//     var csrftoken = $('meta[name="csrf-token"]').attr('content');

//     $('.remove-cart').click(function() {
//         var id = $(this).data("pid").toString();  // Change from attr to data
//         var eml = this;

//         $.ajax({
//             type: "POST",  // Changed to POST for data modification
//             url: "{% url 'remove_cart' %}",  // Use Django URL template tag
//             data: {
//                 prod_id: id
//             },
//             headers: {
//                 'X-CSRFToken': csrftoken  // Include CSRF token in header
//             },
//             success: function(data) {
//                 if (data.error) {
//                     alert(data.error);
//                 } else {
//                     document.getElementById("amount").innerText = data.amount;
//                     document.getElementById("totalamount").innerText = data.totalamount;
//                     $(eml).closest('.cart-item').remove();
//                     window.location.href = "{% url 'cart' %}";  // Ensure this URL is correct
//                 }
//             },
//             error: function() {
//                 alert("An error occurred. Please try again.");
//             }
//         });
//     });
// });




$('.plus-wishlist').click(function(){
    var id=$(this).attr("pid").toString();
    $.ajax({
        type:"GET",
        url:"/pluswishlist",
        data:{
            prod_id:id
        },
        success:function(data){
            //alert(data.message)
            window.location.href = `http://localhost:8000/product-detail/${id}`
        }
    })
})


$('.minus-wishlist').click(function(){
    var id=$(this).attr("pid").toString();
    $.ajax({
        type:"GET",
        url:"/minuswishlist",
        data:{
            prod_id:id
        },
        success:function(data){
            window.location.href = `http://localhost:8000/product-detail/${id}`
        }
    })
})