<?php 
    require 'config/database.php';

    if(isset($_POST['submit'])){
        $author_id = $_SESSION['user-id'];
        $title = $_POST['title'];
        $body = $_POST['body'];
        $category_id = $_POST['category'];
        $is_featured = $_POST['is_featured'];

        $thumbnail = $_FILES['thumbnail'];

        // set is_featured to 0 if unchecked

        $is_featured = $is_featured == 1?1:0;

        // validate form data
        if(!$title){
            $_SESSION['add-post'] = "Enter post title";
        }else if(!$body){
            $_SESSION['add-post'] = "Enter post body";
        }else if(!$category_id){
            $_SESSION['add-post'] = "select post category";
        }else if(!$thumbnail['name']){
            $_SESSION['add-post'] = "Upload thumbnail";
        }else{
            // WORK ON THUMBNAIL
            // rename the image
            $time = time(); // make each image name unique
            $thumbnail_name = $time . $thumbnail['name'];
            $thumbnail_tmp_name = $thumbnail['tmp_name'];
            $thumbnail_destination_path = '../images/'. $thumbnail_name;

            // make sure files is an image
            $allowed_files = ['png', 'jpg', 'jpeg'];
            $extension = explode('.', $thumbnail_name);
            // var_dump($extension);
            $extension = end($extension);
            if(in_array($extension, $allowed_files)){
                // make sure image is not too big. (2mb+)
                if($thumbnail['size'] < 2_000_000){
                    // upload thumbnail
                    move_uploaded_file($thumbnail_tmp_name, $thumbnail_destination_path);
                }else{
                    $_SESSION['add-post'] = "File size is too large. Image should be less than 2mb";
                }
            }else{
                $_SESSION['add-post'] = "File should be png, jpg or jpeg.";
            }
        }
        // var_dump($thumbnail_name);
        // redirect back(with form data) to add-post is there is any problem
        if(isset($_POST['add-post'])){
            $_SESSION['add-post-data'] = $_POST;
            header('location: ' . ROOT_URL . 'admin/add_post.php');
            die();
        }else{
            // set is_featured of all posts to 0 if is_featured for this post is 1
            if($is_featured == 1){
                $zero_all_is_featured_query = "UPDATE posts SET is_featured=0";
                $zero_all_is_featured_result = mysqli_query($connection, $zero_all_is_featured_query);
            }

            // insert post into database
            $query = "INSERT INTO posts(title, body, thumbnail, category_id, author_id, is_featured) VALUES('$title', '$body', '$thumbnail_name', '$category_id', '$author_id', '$is_featured')";
            $result = mysqli_query($connection, $query);

            if(!mysqli_errno(($connection))){
                $_SESSION['add-post-success'] = "New post added successfully";
                header('location: ' . ROOT_URL . 'admin/');
                die();
            }else{
                $_SESSION['add-post'] = mysqli_error($connection);
                header('location: ' . ROOT_URL . 'admin/add-post.php');
                die();
            }
        }

    }
    header('location: ' . ROOT_URL . 'admin/add-post.php');
    die();
?>