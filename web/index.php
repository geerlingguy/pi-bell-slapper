<?php
/**
 * Ding function. It sends the dings.
 *
 * @todo - There is no error handling here currently. It'll act like it dinged
 *   the dinger no matter what happens.
 */
function ding($count = 1, $interval = 0.1, $play_sound = false) {
  $config = yaml_parse_file('/home/pi/pi-bell-slapper/config.yml');

  foreach (range(1, $count) as $i) {
    // Ding the bell.
    system('python3 /home/pi/pi-bell-slapper/bell_slap.py', $retval);

    if ($play_sound) {
      // Play the sound.
      system('python3 /home/pi/pi-bell-slapper/play_sound.py -f ' . $config['sound']['file'], $retval);
    }

    // Wait the interval.
    usleep($interval * 1000000);
  }
}

// Handle a ding that was just submitted.
if (array_key_exists('ding', $_POST) || array_key_exists('ding_plus_sound', $_POST)) {
  $count = (int) filter_var($_POST['dingCount'], FILTER_VALIDATE_INT);
  $interval = (float) filter_var($_POST['dingInterval'], FILTER_VALIDATE_FLOAT);
  $play_sound = isset($_POST['ding_plus_sound']);
  ding($count, $interval, $play_sound);

  // Fill in the status message if we just dinged.
  $status = "<strong>Success!</strong> The bell has been slapped " . $count . " time" . ($count != 1 ? 's' : '') . ".";
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
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3" crossorigin="anonymous">
  <meta name="viewport" content="width=device-width, initial-scale=1">
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
  echo '<div class="alert alert-dismissible alert-success fade show">' . $status . '<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button></div>';
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
              <input type="submit" class="btn btn-secondary" name="ding_plus_sound" id="ding_plus_sound" value="DING + SOUND" />
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
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-ka7Sk0Gln4gmtz2MlQnikT1wXgYsOg+OMhuP+IlRH9sENBO0LRn5q+8nbTov4+1p" crossorigin="anonymous"></script>
  <script>
    setTimeout(function() {
        bootstrap.Alert.getOrCreateInstance(document.querySelector(".alert")).close();
    }, 3000)
  </script>
</body>
</html>
