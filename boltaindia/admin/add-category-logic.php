<?php
    require 'config/database.php';

    if(isset($_POST['submit'])){
        // get form data
        $title = $_POST['title'];
        $description = $_POST['description'];

        if(!$title){
            $_SESSION['add-category'] = "Please enter title";
        }else if(!$description){
            $_SESSION['add-category'] = "Please enter description";
        }

        // redirect back to add category page with form data if there was invalid input
        if(isset($_SESSION['add-category'])){
            $_SESSION['add-category-data'] = $_POST;
            header('location: ' . ROOT_URL . 'admin/add-category.php');
            die();
        }else{
            // insert category into database
            $query = "INSERT INTO categories(title, description) VALUES('$title', '$description')";
            $result = mysqli_query($connection, $query);
            if(mysqli_errno($connection)){
                $_SESSION['add-category'] = "Couldn't add data";
                header('location: '. ROOT_URL . 'admin/add-category.php');
                die();
            }else{
                $_SESSION['add-category-success'] = "Category <strong>$title</strong> added successfully.";
                header('location: '.ROOT_URL.'admin/manage-categories.php');
                die();
            }
        }
    }
?>