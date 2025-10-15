<?php
    include 'partials/header.php';

    // get user form if submit button was clicked
    $firstname = $_SESSION['add-user-data']['firstname'] ?? null;
    $lastname = $_SESSION['add-user-data']['lastname'] ?? null;
    $username = $_SESSION['add-user-data']['username'] ?? null;
    $email = $_SESSION['add-user-data']['email'] ?? null;
    $createpassword = $_SESSION['add-user-data']['createpassword'] ?? null;
    $confirmpassword = $_SESSION['add-user-data']['confirmpassword'] ?? null;

    // delete session data
    unset($_SESSION['add-user-data']);
?>
   <section class="form__section">
    <div class="container form__section-container">
        <h2>Add User</h2>
        <?php if(isset($_SESSION['add-user'])):?>
        <div class="alert__message error">
            <p>
                <?= $_SESSION['add-user'];
                    unset($_SESSION['add-user']);
                ?>
            </p>
        </div>
        <?php endif ?>
        <form action="<?= ROOT_URL?>admin/add-user-logic.php" enctype="multipart/form-data" method="POST">
            <input type="text"  value="<?= $firstname?>" name="firstname" placeholder="First Name" required>
            <input type="text" value="<?= $lastname?>" name="lastname" placeholder="Last Name" required>
            <input type="text" value="<?= $username?>" name="username" placeholder="Username" required>
            <input type="email" value="<?= $email?>" name="email" placeholder="Email" required>
            <input type="password" value="<?= $createpassword?>" name="createpassword" placeholder="Create Password" required>
            <input type="password" value="<?= $confirmpassword?>" name="confirmpassword" placeholder="Confirm Password" required>
            <select name="userrole">
                <option value="0">Author</option>
                <option value="1">Admin</option>
            </select>
            <div class="form__control">
                <label for="avatar">User Avatar</label>
                <input type="file" name="avatar" id="avatar">
            </div>
            <button type="submit" name="submit" class="btn">Add User</button>
        </form>
    </div>
</section>
 <!-- ************END OF FORM***************** -->
<?php
    include '../partials/footer.php';
?>