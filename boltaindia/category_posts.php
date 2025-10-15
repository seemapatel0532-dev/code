<?php
    include 'partials/header.php';
    if($_GET['id']){
        $category_id = $_GET['id'];
        $category_query = "SELECT * FROM categories WHERE id='$category_id'";
        $category_result = mysqli_query($connection, $category_query);
        $category = mysqli_fetch_assoc($category_result);

        // fetch all posts related to this category
        $post_query = "SELECT * FROM posts WHERE category_id='$category_id'";
        $post_result = mysqli_query($connection, $post_query);


    }else{
        header('location: '. ROOT_URL . 'blog.php');
        die();
    }
?>

    <header class="category__title">
        <h2><?= $category['title']?></h2>
    </header>

    <!-- ************END OF CATEGORY TITLE***************** -->
    <?php if(mysqli_num_rows($post_result) > 0){?>
    <section class="posts">
        <div class="container posts__container">
            <?php while($post = mysqli_fetch_assoc($post_result)){ ?>
            <article class="post">
                <div class="post__thumbnail">
                    <img src="./images/<?= $post['thumbnail']?>" alt="">
                </div>
                <div class="post__info">
                    <a href="category_posts.html" class="category__button">Wild Life</a>
                    <h3 class="post__title">
                        <a href="<?= ROOT_URL ?>post.php?id=<?= $post['id']?>"><?= $post['title']?></a>
                    </h3>
                    <p class="post__body"><?= substr($post['body'], 0, 150)?>...</p>
                    <div class="post__author">
                        <?php
                        $user_id = $post['author_id'];
                        $user_query = "SELECT * FROM users WHERE id='$user_id'";
                        $user_result = mysqli_query($connection, $user_query);
                        $user = mysqli_fetch_assoc($user_result);
                    ?>
                    <div class="post__author-avatar">
                        <img src="./images/<?= $user['avatar']?>" alt="aa">
                    </div>
                    <div class="post__author-info">
                        <h5>By: <?= $user['firstname'] ." ".$user['lastname']?></h5>
                        <small><?= date("M d, Y - H:i", strtotime($post['date_time']))?></small>
                    </div>
                </div>
                </div>
            </article>
            <?php }?>
        </div>
    </section>
    <?php }else{ ?>
        <div class="alert__message error lg">
            <?= "No Posts found"?>
        </div>
    <?php } ?>
        <!-- ******************END OF POSTS*********** -->

    <section class="category__buttons">
        <div class="container category__buttons-container">
            <?php
                    $category_query = "SELECT * FROM categories";
                    $category_result = mysqli_query($connection, $category_query);
                    ?>
                    <?php while($category = mysqli_fetch_assoc($category_result)){?>
            <a href="<?= ROOT_URL?>category_posts.php?id=<?= $category['id']?>" class="category__button"><?= $category['title']?></a>
            <?php }?>
        </div>
    </section>
     <!-- ******************END OF CATEGORY*********** -->
    <?php
    include 'partials/footer.php';
?>