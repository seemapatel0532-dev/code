<?php
    include 'partials/header.php';

    // get the user
    if(isset($_GET['id'])){
        $post_id = $_GET['id'];
        $post_query = "SELECT * FROM posts WHERE id='$post_id'";
        $post_result = mysqli_query($connection, $post_query);
        $post = mysqli_fetch_assoc($post_result);
    }else{
        header('location: ' . ROOT_URL . 'admin/');
        die();
    }

    // fetch categories from database
    $category_query = "SELECT * FROM categories";
    $categories = mysqli_query($connection, $category_query);
?>
   <section class="form__section">
     <!-- add post successfully -->
    <?php if(isset($_SESSION['edit-post'])){?>
        <div class="alert__message success container">
            <p>
                <?= $_SESSION['edit-post'];
                    unset($_SESSION['edit-post']);
                ?>
            </p>
        </div>
        <?php }?>
    <div class="container form__section-container">
        <h2>Edit Post</h2>
        <form action="<?= ROOT_URL?>admin/edit-post-logic.php" enctype="multipart/form-data">
            <input type="hidden" name="id" value="<?= $post['id']?>">
            <input type="hidden" name="previous_thumbnail_name" value="<?= $post['thumbnail']?>">
            <input type="text" name="title" value="<?= $post['title']?>" placeholder="Title">
            <select>
                <?php while($category = mysqli_fetch_assoc($categories)){?>
                <option value="<?= $category['id']?>"><?= $category['title']?></option>
                <?php } ?>
            </select>
            <textarea rows="10" name="body" placeholder="Body"><?= $post['body']?></textarea>
             <div class="form__control inline">
                <input type="checkbox" name="is_featured" id="is_featured" <?= ($post['is_featured'] == 1) ? 'checked' : '' ?>>
                <label for="is_featured">Featured</label>
            </div>
            <div class="form__control">
                <label for="thumbnail">Change Thumbnail</label>
                <input type="file" name="thumbnail" id="thumbnail">
            </div>
            <button type="submit" name="submit" class="btn">Update Post</button>
        </form>
    </div>
</section>
<?php
    include '../partials/footer.php';
?>