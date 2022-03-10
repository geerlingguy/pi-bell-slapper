<?php
/**
 * Ding function. It sends the dings.
 */
function ding($count = 1, $interval = 0.1) {
  system('python3 /home/pi/pi-bell-slapper/bell_slap.py -c ' . $count . ' -i ' . $interval, $retval);
}

// See if a ding was just submitted.
if (array_key_exists('ding', $_POST)) {
  $count = (int) filter_var($_POST['dingCount'], FILTER_VALIDATE_INT);
  $interval = (float) filter_var($_POST['dingInterval'], FILTER_VALIDATE_FLOAT);
  ding($count, $interval);

  // Fill in the status message if we just dinged.
  $status = "<strong>Success!</strong> The bell has been slapped.";
}
else {
  $count = (int) 1;
  $interval = (float) 1.0;
}
?>
<!DOCTYPE html>
<html>
<head>
  <title>Pi Bell Slapper - Control Panel</title>
  <!-- TODO Add the stylesheet to the project. No CDN. -->
  <link rel="stylesheet" type="text/css" href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" media="screen" />
</head>
<body>
  <div class="container">
    <div class="row">
      <div class="col-sm-3">
        &nbsp;
      </div>
      <div class="col-sm-6">
        <div class="text-center my-1">
          <h1>&#128276; Bell Control</h1>
        </div>
<?php
if (isset($status)) {
  echo '<div class="alert alert-success">' . $status . '</div>';
}
?>
        <div class="card">
          <div class="card-body">
            <h5 class="card-title">Ding the Bell!</h5>
            <form method="post">
              <div class="form-group py-2">
                <label for="dingCount">Ding Count</label>
                <input type="text" class="form-control" name="dingCount" id="dingCount" value="<?php echo $count; ?>">
                <small id="dingCountHelp" class="form-text text-muted">How many dings should I do?</small>
              </div>

              <div class="form-group py-2">
                <label for="dingInterval">Ding Interval (seconds):</label>
                <input type="text" class="form-control"  name="dingInterval" id="dingInterval" value="<?php echo number_format($interval, 2); ?>">
                <small id="dingIntervalHelp" class="form-text text-muted">Interval between dings, in seconds (example: 1.00).</small>
              </div>

              <input type="submit" class="btn btn-primary" name="ding" id="ding" value="DING" />
            </form>
          </div>
        </div>
        <div class="card my-2">
          <div class="card-body text-center">
            &#128519; Made by <a href="https://www.jeffgeerling.com/">Jeff Geerling</a>.
          </div>
        </div>
      </div>
      <div class="col-sm-3">
        &nbsp;
      </div>
    </div>
  </div>
</body>
</html>
