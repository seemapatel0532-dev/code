<?php
    include 'partials/header.php';

    // fetch featured post from database
    $featured_query = "SELECT * FROM posts WHERE is_featured=1";
    $featured_result = mysqli_query($connection, $featured_query);
    $featured = mysqli_fetch_assoc($featured_result);


    // search
    $search = $_GET['search'] ?? '';

    if ($search) {
        $search = mysqli_real_escape_string($connection, $search);
        $query = "SELECT * FROM posts WHERE title LIKE '%$search%' OR body LIKE '%$search%' ORDER BY date_time DESC";
    } else {
        $query = "SELECT * FROM posts ORDER BY date_time DESC";
    }
    $posts = mysqli_query($connection, $query);

?>
    <section class="search__bar">
        <form action="<?= ROOT_URL ?>blog.php" method="GET" class="container search__bar-container">
        <div>
            <i class="uil uil-search"></i>
            <input type="search" name="search" placeholder="Search posts...">
        </div>
        <button class="btn" type="submit">Go</button>
    </form>
    </section>
    <!-- ******************END OF SEARCH*********** -->
     <?php if(mysqli_num_rows($posts) > 0){?>
    <section class="posts">
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