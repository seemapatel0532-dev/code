<?php
    require 'config/database.php';

    // fetch current user from database
    if(isset($_SESSION['user-id'])){
        $id = $_SESSION['user-id'];
        $query = "SELECT avatar FROM users WHERE ID='$id'";
        $result = mysqli_query($connection, $query);
        $avatar = mysqli_fetch_assoc($result);
    }
?>

<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- LOGO -->
    <link rel="icon" type="" href="<?php echo ROOT_URL?>assets/boltaindia2.png">
    <title>BoltaIndia</title>
    <!-- CUSTOM STYLESHEET -->
    <link rel="stylesheet" href="<?php echo ROOT_URL?>css/style.css">
    <!-- ICONSOUT CDN -->
    <link rel="stylesheet" href="https://unicons.iconscout.com/release/v4.0.0/css/line.css">
    <!-- Google  Montserrat-->
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800;900&display=swap">
    
</head>
<body> 
    <nav>
        <div class="container nav__container">
            <a href="<?php echo ROOT_URL?>" class="nav__logo">Bolta-India</a>
            <ul class="nav__items">
                <li><a href="<?php echo ROOT_URL?>blog.php">Blog</a></li>
                <li><a href="<?php echo ROOT_URL?>about.php">About</a></li>
                <li><a href="<?php echo ROOT_URL?>services.php">Services</a></li>
                <li><a href="<?php echo ROOT_URL?>contact.php">Contact</a></li>
                <?php if(isset($_SESSION['user-id'])){?>
                <li class="nav__profile">
                    <div class="avatar"><img src="<?= ROOT_URL . 'images/' . $avatar['avatar']?>" alt="BoltaIndia"></div>
                    <ul>
                        <li><a href="<?php echo ROOT_URL?>admin/">Dashboard</a></li>
                        <li><a href="<?php echo ROOT_URL?>logout.php">Log Out</a></li>
                    </ul>
                </li>
                <?php }else{?>
                    <li><a href="<?= ROOT_URL?>signin.php">Sign In</a></li>
                    <?php } ?>
            </ul>

            <button id="open__nav-btn"><i class="uil uil-bars"></i></button>
            <button id="close__nav-btn"><i class="uil uil-multiply"></i></button>
        </div>
    </nav>
    <!-- ************END OF NAV***************** -->