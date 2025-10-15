<?php
    require 'config/database.php';
    if(isset($_POST['submit'])){
        // get updated form data
        $id = $_POST['id'];
        $firstname = $_POST['firstname'];
        $lastname = $_POST['lastname'];
        $is_admin = $_POST['userrole'];

        // check for valid input
        if(!$firstname || !$lastname){
            $_SESSION['edit-user'] = "Invalid Form Input on edit page. ";
            header('location: ' . ROOT_URL . 'admin/edit-user.php');
            die();
        }else{
            // update user
            $query = "UPDATE users SET firstname='$firstname', lastname='$lastname', is_admin='$is_admin' WHERE id='$id' LIMIT 1";
            $result = mysqli_query($connection, $query);

            if(mysqli_errno($connection)){
                $_SESSION['edit-user'] = "Failed to update user.";
            }else{
                $_SESSION['edit-user-success'] = "User <strong>$firstname $lastname</strong> updated successfully";
            }
        }
    }
    header('location: ' . ROOT_URL . 'admin/manage-users.php');
    die();
?>