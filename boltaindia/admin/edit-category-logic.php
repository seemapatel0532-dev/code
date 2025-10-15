<?php
    require 'config/database.php';
    if(isset($_POST['submit'])){
        $id = $_POST['id'];
        $title = $_POST['title'];
        $description = $_POST['description'];
        if(!$title){
            $_SESSION['edit-category'] = "Please enter the title";
        }else if(!$description){
            $_SESSION['edit-category'] = "Please enter the description";
        }else{
            // update category
            $query = "UPDATE categories SET title='$title', description='$description' WHERE id='$id'";
            $result = mysqli_query($connection, $query);
            if(mysqli_errno($connection)){
                $_SESSION['edit-user'] = "Failed to update category";
            }else{
                $_SESSION['edit-category-success'] = "Category <strong>$title</strong> updated successfully";
            }
        }
    }
    header('location: '.ROOT_URL. 'admin/manage-categories.php');
    die();
?>