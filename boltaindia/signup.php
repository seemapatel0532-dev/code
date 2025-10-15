<?php
    require 'config/constants.php';

    // get back from data if there was a registration error
    $firstname = $_SESSION['signup-data']['firstname'] ?? null;
    $lastname = $_SESSION['signup-data']['lastname'] ?? null;
    $username = $_SESSION['signup-data']['username'] ?? null;
    $email = $_SESSION['signup-data']['email'] ?? null;
    $createpassword = $_SESSION['signup-data']['createpassword'] ?? null;
    $confirmpassword = $_SESSION['signup-data']['confirmpassword'] ?? null;
    unset($_SESSION['signup-data']);
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
    <link rel="stylesheet" href="<?php echo ROOT_URL;?>/css/style.css">
    <!-- ICONSOUT CDN -->
    <link rel="stylesheet" href="https://unicons.iconscout.com/release/v4.0.0/css/line.css">
    <!-- Google  Montserrat-->
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800;900&display=swap">
    
</head>
<body>

   <section class="form__section">
    <div class="container form__section-container">
        <h2>Sign Up</h2>
        <?php if(isset($_SESSION['signup'])):?>
        <div class="alert__message error">
            <p>
                <?= $_SESSION['signup'];
                    unset($_SESSION['signup']);
                ?>
            </p>
        </div>
        <?php endif ?>
        <form action="<?php echo ROOT_URL ?>signup-logic.php" enctype="multipart/form-data" method="POST">
            <input type="text" value="<?= $firstname?>" name="firstname" placeholder="First Name" required>
            <input type="text" value="<?= $lastname?>" name="lastname" placeholder="Last Name" required>
            <input type="text" value="<?= $username?>" name="username" placeholder="Username" required>
            <input type="email" value="<?= $email?>" name="email" placeholder="Email" required>
            <input type="password" value="<?= $createpassword?>" name="createpassword" placeholder="Create Password" required>
            <input type="password" value="<?= $confirmpassword?>" name="confirmpassword" placeholder="Confirm Password" required>
            <div class="form__control">
                <label for="avatar"></label>
                <input type="file" name="avatar" id="avatar">
            </div>
            <button type="submit" name="submit" class="btn">Sign Up</button>
            <small>Already have an account? <a href="signin.php">Sign In</a></small>
        </form>
    </div>
</section>
<script src="<?php echo ROOT_URL?>js/main.js"></script>
</body>
</html>
