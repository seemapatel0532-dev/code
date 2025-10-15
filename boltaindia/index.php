<?php
    include 'partials/header.php';

    // fetch featured post from database
    $featured_query = "SELECT * FROM posts WHERE is_featured=1";
    $featured_result = mysqli_query($connection, $featured_query);
    $featured = mysqli_fetch_assoc($featured_result);

    // fetch 9 posts from posts table
    $query = "SELECT * FROM posts ORDER BY date_time DESC LIMIT 9";
    $posts = mysqli_query($connection, $query);
?>
<!-- SHOW FEATURED POSTS IF THERE IS ANY -->
<?php if(mysqli_num_rows($featured_result) == 1){?>
    <section class="featured">
        <article class="container featured__container">
            <div class="post__thumbnail">
                <img src="./images/<?= $featured['thumbnail']?>" alt="">
            </div>
            <div class="post__info">
                <?php
                    $category_id = $featured['category_id'];
                    $category_query = "SELECT title FROM categories WHERE id='$category_id'";
                    $category_result = mysqli_query($connection, $category_query);
                    $category = mysqli_fetch_assoc($category_result);
                ?>
                <a href="<?= ROOT_URL?>category_posts.php?id=<?= $category_id?>" class="category__button"><?= $category['title']?></a>
                <h2 class="post__title"><a href="<?= ROOT_URL ?>post.php?id=<?= $featured['id']?>"><?= $featured['title']?></a></h2>
                <p class="post__body"><?= substr($featured['body'], 0, 300)?>...</p>
                <div class="post__author">
                    <?php
                        $user_id = $featured['author_id'];
                        $user_query = "SELECT * FROM users WHERE id='$user_id'";
                        $user_result = mysqli_query($connection, $user_query);
                        $user = mysqli_fetch_assoc($user_result);
                    ?>
                    <div class="post__author-avatar">
                        <img src="./images/<?= $user['avatar']?>" alt="">
                    </div>
                    <div class="post__author-info">
                        <h5>By: <?= $user['firstname'] ." ".$user['lastname']?></h5>
                        <small><?= date("M d, Y - H:i", strtotime($featured['date_time']))?></small>
                    </div>
                </div>
            </div>
        </article>
    </section>
    <?php }?>
    <!-- ******************END OF FEATURED*********** -->
    <section class="posts<?= $featured ? '' : 'section__extra-margin' ?>">
        <div class="container posts__container">
            <?php while($post = mysqli_fetch_assoc($posts)){?>
            <article class="post">
                <div class="post__thumbnail">
                    <img src="./images/<?= $post['thumbnail']?>" alt="">
                </div>
                <div class="post__info">
                    <?php
                        $category_id = $post['category_id'];
                        $category_query = "SELECT title FROM categories WHERE id='$category_id'";
                        $category_result = mysqli_query($connection, $category_query);
                        $category = mysqli_fetch_assoc($category_result);
                    ?>
                    <a href="<?= ROOT_URL?>category_posts.php?id=<?= $category_id?>" class="category__button"><?= $category['title']?></a>
                    <h3 class="post__title">
                        <a href="<?= ROOT_URL?>post.php?id=<?= $post['id']?>"><?= $post['title']?></a>
                    </h3>
                    <p class="post__body"><?= substr($post['body'], 0, 150)?>...</p>
                    <div class="post__author">
                    <div class="post__author-avatar">
                        <img src="./images/avatar2.jpg" alt="">
                    </div>
                    <div class="post__author">
                    <?php
                        $user_id = $post['author_id'];
                        $user_query = "SELECT * FROM users WHERE id='$user_id'";
                        $user_result = mysqli_query($connection, $user_query);
                        $user = mysqli_fetch_assoc($user_result);
                    ?>
                    <div class="post__author-avatar">
                        <img src="./images/<?= $user['avatar']?>" alt="">
                    </div>
                    <div class="post__author-info">
                        <h5>By: <?= $user['firstname'] ." ".$user['lastname']?></h5>
                        <small><?= date("M d, Y - H:i", strtotime($post['date_time']))?></small>
                    </div>
                </div>
                </div>
                </div>
            </article>
            <?php }?>
        </div>
    </section>
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

