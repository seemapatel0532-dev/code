<?php
    require 'config/database.php';
    if(isset($_POST['submit'])){
        // get form data
        $username_email = $_POST['username_email'];
        $password = $_POST['password'];

        if(!$username_email){
            $_SESSION['signin'] = "Username or Email is required";
        }else if(!$password){
            $_SESSION['signin'] = "Password is required";
        }else{
            // fetch user from database
            $fetch_user_query = "SELECT * FROM users WHERE username='$username_email' OR email='$username_email'";
            $fetch_user_result = mysqli_query($connection, $fetch_user_query);
            
            if(!$fetch_user_result){
                $_SESSION['signin'] = "Query Error";
                header('location: '. ROOT_URL .'signin.php');
                die();
            }

            if(mysqli_num_rows($fetch_user_result) == 1){
                // convert record in assoc array
                $user_record = mysqli_fetch_assoc($fetch_user_result);
                $db_password = $user_record['password'];
                // compare the password
                if(password_verify($password, $db_password)){
                    // set session for access control
                    $_SESSION['user-id'] = $user_record['id'];
                    // set session if user is an admin
                    if($user_record['is_admin'] == 1){
                        $_SESSION['user_is_admin'] = true;
                    }
                    // log user in
                    header('location: ' . ROOT_URL . 'admin/');
                }else{
                    $_SESSION['signin'] = "Please check your input";
                }
            }else{
                $_SESSION['signin'] = "User not found";
            }
        }
        // if any problem, redirect back to signin page with login data
        if(isset($_SESSION['signin'])){
            $_SESSION['signin-data'] = $_POST;
            header('location: ' . ROOT_URL . 'signin.php');
            die();
        }
    }else{
        header('location: '. ROOT_URL .'signin.php');
        die();
    }
?>