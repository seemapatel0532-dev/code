<?php
    include 'partials/header.php';
    if($_GET['id']){
        $post_id = $_GET['id'];
        $post_query = "SELECT * FROM posts WHERE id='$post_id'";
        $post_result = mysqli_query($connection, $post_query);
        $post = mysqli_fetch_assoc($post_result);

        // Author details
        $user_id = $post['author_id'];
        $user_query = "SELECT * FROM users WHERE id='$user_id'";
        $user_result = mysqli_query($connection, $user_query);
        $user = mysqli_fetch_assoc($user_result);


    }else{
        header('location: '. ROOT_URL . 'blog.php');
        die();
    }
?>
    <section class="singlepost">
        <div class="container singlepost__container">
            <h2><?= $post['title']?></h2>
            <div class="post__author">
                <div class="post__author-avatar">
                    <img src="./images/<?= $user['avatar']?>" alt="">
                </div>
                <div class="post__author-info">
                    <h5>By: <?= $user['firstname'] . ' ' . $user['lastname']?></h5>
                    <small><?= date("M d, Y - H:i", strtotime($post['date_time']))?></small>
                </div>
            </div>
            <div class="singlepost__thumbnail">
                <img src="./images/<?= $post['thumbnail']?>" alt="">
            </div>
            <p><?= $post['body']?></p>
        </div>
    </section>
      <!-- ************END OF SINGLEPOST***************** -->
<?php
    include 'partials/footer.php';
?>