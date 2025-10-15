<?php
    require 'config/database.php';
// get signup form data if signup button was clicked

if(isset($_POST['submit'])){
    $firstname = $_POST['firstname'];
    $lastname = $_POST['lastname'];
    $email = $_POST['email'];
    $username = $_POST['username'];
    $createpassword = $_POST['createpassword'];
    $confirmpassword = $_POST['confirmpassword'];
    $avatar = $_FILES['avatar'];
    // echo $firstname . $lastname . $email . $createpassword . $confirmpassword;
    // var_dump($avatar);
    // validate input values
    if(!$firstname){
        $_SESSION['signup'] = "Please enter your first name";
    }else if(!$lastname){
        $_SESSION['signup'] = "Please enter your last name";
    }else if(!$username){
        $_SESSION['signup'] = "Please enter your username";
    }else if(!$email){
        $_SESSION['signup'] = "Please enter your email";
    }else if(strlen($createpassword) < 8 || strlen($confirmpassword) < 8){
        $_SESSION['signup'] = "Password should be 8 characters";
    }else if(!$avatar['name']){
        $_SESSION['signup'] = "Please add avatar";
    }else{
        // check if passswords don't match
        if($createpassword !== $confirmpassword){
            $_SESSION['signup'] = "Password don't matched";
        }else{
            // hashed password
            $hashed_password = password_hash($createpassword, PASSWORD_DEFAULT);
            // echo $createpassword . '<br/>' . $hashed_password;

            // check if username or email already exit in database
            $user_check_query = "SELECT * FROM users WHERE username = '$username' OR email = '$email'";
            $user_check_result = mysqli_query($connection, $user_check_query);
            if(mysqli_num_rows($user_check_result) > 0){
                $_SESSION['signup'] = "Username or Email already exit";
            }else{
                // WORK ON AVATAR
                // rename avatar
                $time = time(); // make each image name unique current timestamp
                // echo $time;
                $avatar_name = $time . $avatar['name'];
                $avatar_tmp_name = $avatar['tmp_name'];
                $avatar_destination_path = 'images/' . $avatar_name;

                // make sure file is an image
                $allowed_files = ['jpg', 'png', 'jpeg'];
                $extention = explode('.', $avatar_name);
                $extention = end($extention);
                if(in_array($extention, $allowed_files)){
                    // make sure image is not too large(1mb+)
                    if($avatar['size'] < 1000000){
                        // upload avatar
                        move_uploaded_file($avatar_tmp_name, $avatar_destination_path);
                    }else{
                        $_SESSION['signup'] = 'Files size too big. Should be less than 1mb';
                    }
                }else{
                    $_SESSION['signup'] = "File should be png, jpg or jpeg";
                }
            }
        }
    }
    // redirect back to signup page if there was any problem
    if($_SESSION['signup']){
        // pass from data back to signup page
        $_SESSION['signup-data'] = $_POST;
        header('location: '. ROOT_URL . 'signup.php');
        die();
    }else{
        $insert_user_query = "INSERT INTO users(firstname, lastname, username, email, password, avatar, is_admin) VALUES('$firstname', '$lastname', '$username', '$email', '$hashed_password', '$avatar_name', 0);";

        $insert_user_result = mysqli_query($connection, $insert_user_query);

        if(!mysqli_errno($connection)){
            // redirect to login page with success message
            $_SESSION['signup-success'] = "Registeration successfully. Please log in ";
            header('location: '. ROOT_URL . 'signin.php');
            die();
        }
    }

}else{
    // if button wasn't clicked, bounce back 
    header('location: '.ROOT_URL.'signup.php');
    die();
}
?>