<?php
    include 'partials/header.php';

    // fetch users from database but not current user
    $current_admin_id = $_SESSION['user-id'];
    $query = "SELECT * FROM users WHERE NOT id = '$current_admin_id' ORDER BY id DESC";
    $users = mysqli_query($connection, $query);
?>
    
<section class="dashboard">
    <?php if(isset($_SESSION['add-user-success'])){?>
        <div class="alert__message success container">
            <p>
                <?= $_SESSION['add-user-success'];
                    unset($_SESSION['add-user-success']);
                ?>
            </p>
        </div>
        <?php }else if(isset($_SESSION['edit-user-success'])){?>
        <div class="alert__message success container">
            <p>
                <!-- show if edit user was successfull -->
                <?= $_SESSION['edit-user-success'];
                    unset($_SESSION['edit-user-success']);
                ?>
            </p>
        </div>
        <?php }else if(isset($_SESSION['edit-user'])){?>
        <div class="alert__message error container">
            <p>
                <!-- show if edit user was not successfull -->
                <?= $_SESSION['edit-user'];
                    unset($_SESSION['edit-user']);
                ?>
            </p>
        </div>
        <?php }else if(isset($_SESSION['delete-user-success'])){?>
        <div class="alert__message success container">
            <p>
                <!-- show if edit user was successfull -->
                <?= $_SESSION['delete-user-success'];
                    unset($_SESSION['delete-user-success']);
                ?>
            </p>
        </div>
        <?php }else if(isset($_SESSION['delete-user'])){?>
        <div class="alert__message error container">
            <p>
                <!-- show if edit user was not successfull -->
                <?= $_SESSION['delete-user'];
                    unset($_SESSION['delete-user']);
                ?>
            </p>
        </div>
        <?php }?>
    <div class="container dashboard__container">
        <button id="show__sidebar-btn" class="sidebar__toggle"><i class="uil uil-angle-right-b"></i></button>
        <button id="hide__sidebar-btn" class="sidebar__toggle"><i class="uil uil-angle-left-b"></i></button>
        
        <aside>
            <ul>
                <li><a href="<?= ROOT_URL?>admin/add-post.php"><i class="uil uil-pen"></i><h5>Add Post</h5></a></li>
                <li><a href="<?= ROOT_URL?>admin/"><i class="uil uil-postcard"></i><h5>Manage Post</h5></a></li>
                <?php if(isset($_SESSION['user_is_admin'])){?>
                <li><a href="<?= ROOT_URL?>admin/add-user.php"><i class="uil uil-user-plus"></i><h5>Add User</h5></a></li>
                <li><a href="<?= ROOT_URL?>admin/manage-users.php" class="active"><i class="uil uil-users-alt"></i><h5>Manage Users</h5></a></li>
                <li><a href="<?= ROOT_URL?>admin/add-category.php"><i class="uil uil-edit"></i><h5>Add category</h5></a></li>
                <li><a href="<?= ROOT_URL?>admin/manage-categories.php"><i class="uil uil-list-ul"></i><h5>Manage Categories</h5></a></li>
                <?php } ?>
            </ul>
        </aside>
        <main>
            <h2>Manage Users</h2>
            <?php if(mysqli_num_rows($users)>0){ ?>
            <table>
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Username</th>
                        <th>Edit</th>
                        <th>Delete</th>
                        <th>Admin</th>
                    </tr>
                </thead>
                <tbody>
                    <?php while($user = mysqli_fetch_assoc($users)){?>
                    <tr>
                        <td><?= $user['firstname'] . ' ' .  $user['lastname']?></td>
                        <td><?= $user['username']?></td>
                        <td><a href="<?= ROOT_URL?>admin/edit-user.php?id=<?= $user['id']?>" class="btn sm">Edit</a></td>
                        <td><a href="<?= ROOT_URL?>admin/delete-user.php?id=<?= $user['id']?>" class="btn sm danger">Delete</a></td>
                        <td><?= $user['is_admin'] ? 'Yes' : 'No' ?></td>
                    </tr>
                    <?php } ?>
                </tbody>
            </table>
            <?php }else{ ?>
                <div class="alert__message error">
                    <?= "No users found"?>
                </div>
                <?php } ?>
        </main>
    </div>
</section>
 <!-- ************END OF DASHBOARD***************** -->
    <?php
    include '../partials/footer.php';
?>