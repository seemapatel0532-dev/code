<?php
    require 'config/database.php';

    // make sure edit post button was clicked
    if(isset($_POST['submit'])){
        $id = $_POST['id'];
        $previous_thumbnail_name = $_POST['previous_thumbnail_name'];
        $title = $_POST['title'];
        $body = $_POST['body'];
        $category_id = $_POST['category'];
        $is_featured = $_POST['is_featured'];
        $thumbnail = $_FILES['thumbnail'];

        // set is_featured to 0 if it was checked
        $is_featured = $is_featured == 1 ? 1 : 0;

        // check and validate input values
        if(!$title || !$body || !$category_id || !$is_featured || !$thumbnail['name']){
            $_SESSION['edit-post'] = "Couldn't update post. Invalid form data on edit post page";
        }else{
            if($thumbnail['name']){
                $previous_thumbnail_path = '../images' . $previous_thumbnail_name;
                if($previous_thumbnail_path){
                    unlink($previous_thumbnail_path);
                }

                // WORK ON THUMBNAIL
                // rename image
                $time = time();
                $thumbnail_name = $time . $thumbnail['name'];
                $thumbnail_tmp_name = $thumbnail['tmp_name'];
                $thumbnail_destination_path = '../images/' . $thumbnail_name;

                // make sure file is an image
                $allowed_files = ['png', 'jpg', 'jpeg'];
                $extension = explode('.', $thumbnail_name);
                $extension = end($extension);
                if(in_array($extension, $allowed_files)){
                    // make sure image is not too large
                    if($thumbnail['size']<2000000){
                        // upload image
                        move_uploaded_file($thumbnail_tmp_name, $thumbnail_destination_path);
                    }else{
                        $_SESSION['edit-post'] = "Couldn't update post. thumbnail size is too large";
                    }
                }else{
                    $_SESSION['edit-post'] = "Couldn't update post. Thumbnail should be png, jpg or jpeg";
                }
            }
        }
        if($_SESSION['edit-post']){
            // redirect to manage form page if form was invalid
            header('location: ' . ROOT_URL . 'admin/edit-post.php');
            die();
        }else{
            // set is_featured of all posts to 0 if is_featured for this post is 1
            if($is_featured == 1){
                $zero_all_is_featured_query = "UPDATE posts SET is_featured=0";
                $zero_all_is_featured_result = mysqli_query($connection, $zero_all_is_featured_query);
            }

            // set thumbnail name if a new one was uploaded, else keep old thumbnail name
            $thumbnail_to_insert = $thumbnail_name ?? $previous_thumbnail_name;

            // insert post into database
            $query = "UPDATE posts SET title='$title', body='$body', thumbnail='$thumbnail_to_insert', category_id='$category_id', is_featured='$is_featured' WHERE id='$id'";
            $result = mysqli_query($connection, $query);

            if(!mysqli_errno(($connection))){
                $_SESSION['edit-post-success'] = "Post updated successfully";
                header('location: ' . ROOT_URL . 'admin/manage-users.php');
                die();
            }else{
                $_SESSION['add-post'] = mysqli_error($connection);
                header('location: ' . ROOT_URL . 'admin/edit-post.php');
                die();
            }
        }

    }
    header('location: ' . ROOT_URL . 'admin/edit-post.php');
    die();
?>