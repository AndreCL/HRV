package eu.luanca.hrv;

/**
 * Created by andre_000 on 17-09-2015.
 * This activity is where you interact with the device.
 * 1. Make sure the device is paired with the phone
 * 2. Open app and put on sensor
 * 3. If connection doesn't work, reconnect with button 1
 * 4. To save the data to a file, press button 2
 * 5. To Stop saving data, press button 2 again
 * The file is saved in downloads.
 * Todo:
 * Fix location. Some issues on certain devices that doesn't allow to update the location constantly
 */

import android.app.Activity;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.content.Context;
import android.content.Intent;
import android.location.Location;
import android.location.LocationManager;
import android.os.Bundle;
import android.os.Environment;
import android.os.Handler;
import android.os.Message;
import android.os.PowerManager;
import android.util.Log;
import android.view.View;
import android.view.Window;
import android.widget.ImageButton;
import android.widget.TextView;
import android.widget.Toast;

import com.google.android.gms.common.ConnectionResult;
import com.google.android.gms.common.api.GoogleApiClient;
import com.google.android.gms.location.LocationListener;
import com.google.android.gms.location.LocationRequest;
import com.google.android.gms.location.LocationServices;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Set;

public class MainActivity extends Activity implements
        GoogleApiClient.ConnectionCallbacks,
        GoogleApiClient.OnConnectionFailedListener,
        LocationListener {

    private Context mContext;
    private boolean isRecording = false;
    private String recordingTag;

    //buttons
    ImageButton scan, rec;

    //for location
    private GoogleApiClient mGoogleApiClient;
    private LocationRequest mLocationRequest;
    double currentLatitude, currentLongitude;
    private LocationManager locMan;
    private LocationListener loclist;

    /*
     *  TAG for Debugging Log
     */
    private static final String TAG = "ZephyrLogger";

    /*
     *  Layout Views
     */
    private TextView mStatus;
    private TextView battery;

    /*
     * Name of the connected device, and it's address
     */
    private String mHxMName = null;
    private String mHxMAddress = null;

    /*
     * Local Bluetooth adapter
     */
    private BluetoothAdapter mBluetoothAdapter = null;

    /*
     * Member object for the chat services
     */
    private HxmService mHxmService = null;

    /* Checks if external storage is available for read and write */
    public boolean isExternalStorageWritable() {
        String state = Environment.getExternalStorageState();
        if (Environment.MEDIA_MOUNTED.equals(state)) {
            return true;
        }
        return false;
    }

    public File exportData(HrmReading m) {
        // Get the directory for the user's downloads directory.
        File path = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS);
        //File file = new File(path, "Zephyr_"+recordingTag+"_data.txt"); //default
        File file = new File(path, "HRV.txt"); //make sure it appends instead of overwrites
        try {
            if (!file.exists()) {
                file.createNewFile();
            }
            FileWriter writer = new FileWriter(file, true);
            writer.write(System.currentTimeMillis() + "," + m.toString() + "," + currentLatitude + "," + currentLongitude + "\n");
            writer.close();
        } catch (IOException e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
        }
        return file;
    }

    /*
     * connectToHxm() sets up our service loops and starts the connection
     * logic to manage the HxM device data stream
     */
    private void connectToHxm() {
		/*
		 * Update the status to connecting so the user can tell what's happening
		 */
        mStatus.setText(R.string.connecting);

		/*
		 * Setup the service that will talk with the Hxm
		 */
        if (mHxmService == null)
            setupHrm();

		/*
		 * Look for an Hxm to connect to, if none is found tell the user
		 * about it
		 */
        if (getFirstConnectedHxm()) {
            BluetoothDevice device = mBluetoothAdapter.getRemoteDevice(mHxMAddress);
            mHxmService.connect(device);    // Attempt to connect to the device
        } else {
            mStatus.setText(R.string.nonePaired);
        }

    }


    /*
     * Loop through all the connected bluetooth devices, the first one that
     * starts with HXM will be assumed to be our Zephyr HxM Heart Rate Monitor,
     * and this is the device we will connect to
     *
     * returns true if a HxM is found and the global device address has been set
     */
    private boolean getFirstConnectedHxm() {

		/*
		 * Initialize the global device address to null, that means we haven't
		 * found a HxM to connect to yet
		 */
        mHxMAddress = null;
        mHxMName = null;


		/*
		 * Get the local Bluetooth adapter
		 */
        BluetoothAdapter mBtAdapter = BluetoothAdapter.getDefaultAdapter();

		/*
		 *  Get a set of currently paired devices to cycle through, the Zephyr HxM must
		 *  be paired to this Android device, and the bluetooth adapter must be enabled
		 */
        Set<BluetoothDevice> bondedDevices = mBtAdapter.getBondedDevices();

		/*
		 * For each device check to see if it starts with HXM, if it does assume it
		 * is the Zephyr HxM device we want to pair with
		 */
        if (bondedDevices.size() > 0) {
            for (BluetoothDevice device : bondedDevices) {
                String deviceName = device.getName();
                if (deviceName.startsWith("HXM")) {
					/*
					 * we found an HxM to try to talk to!, let's remember its name and
					 * stop looking for more
					 */
                    mHxMAddress = device.getAddress();
                    mHxMName = device.getName();
                    Log.d(TAG, "getFirstConnectedHxm() found a device whose name starts with 'HXM', its name is " + mHxMName + " and its address is ++mHxMAddress");
                    break;
                }
            }
        }

		/*
		 * return true if we found an HxM and set the global device address
		 */
        return (mHxMAddress != null);
    }

    /*
     * Our onCreate() needs to setup the main activity that we will use to
     * @see android.app.Activity#onCreate(android.os.Bundle)
     */
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        Log.e(TAG, "onCreate");

        mContext = getApplicationContext();

		/*
		 * Set up the window layout, we can use a cutom title, the layout
		 * from our resource file
		 */
        this.requestWindowFeature(Window.FEATURE_NO_TITLE);
        setContentView(R.layout.activity_main);

        //map
        buildGoogleApiClient();
        //get location
        // Create the LocationRequest object
        createLocationRequest();

		/*
		 *  Set up the status text view, if we can't do it something is wrong with
		 *  how this application package was built, in that case display a message
		 *  and give up.
		 */
        mStatus = (TextView) findViewById(R.id.status);
        if (mStatus == null) {
            Toast.makeText(this, "Something went very wrong, missing resource, rebuild the application", Toast.LENGTH_LONG).show();
            finish();
        }
        battery = (TextView) findViewById(R.id.batteryChargeIndicator);


		/*
		 *  Get the default bluetooth adapter, if it fails there is not much we can do
		 *  so show the user a message and then close the application
		 */
        mBluetoothAdapter = BluetoothAdapter.getDefaultAdapter();

		/*
		 *  If the adapter is null, then Bluetooth is not supported
		 */
        if (mBluetoothAdapter == null) {
			/*
			 * Blutoooth needs to be available on this device, and also enabled.
			 */
            Toast.makeText(this, "Bluetooth is not available or not enabled", Toast.LENGTH_LONG).show();
            mStatus.setText(R.string.noBluetooth);

        } else {
			/*
			 * Everything should be good to go so let's try to connect to the HxM
			 */
            if (!mBluetoothAdapter.isEnabled()) {
                mStatus.setText(R.string.btNotEnabled);
                Log.d(TAG, "onStart: Blueooth adapter detected, but it's not enabled");
            } else {
                mStatus.setText(R.string.connecting);
                connectToHxm();
            }
        }

        /*Report status*/
        scan = (ImageButton) findViewById(R.id.scanbutton);
        scan.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                connectToHxm();
            }
        });

        /*Report status*/
        rec = (ImageButton) findViewById(R.id.recbutton);
        rec.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {

                isRecording = (isRecording ? false : true);
                recordingTag = (isRecording ? "" + System.currentTimeMillis() : recordingTag);
                Toast.makeText(mContext,
                        (isRecording ? R.string.recording_on : R.string.recording_off),
                        Toast.LENGTH_LONG).show();
            }
        });

        /*keep screen on*/
        PowerManager pm = (PowerManager) getSystemService(Context.POWER_SERVICE);
        PowerManager.WakeLock wl = pm.newWakeLock(PowerManager.SCREEN_DIM_WAKE_LOCK, "My Tag");
        wl.acquire();

// screen and CPU will stay awake during this section

        wl.release();
    }

    @Override
    public void onStart() {
        super.onStart();
        Log.d(TAG, "onStart");

		/*
		 * Check if there is a bluetooth adapter and if it's enabled,
		 * error messages and status updates as appropriate
		 */
        if (mBluetoothAdapter != null) {
            // If BT is not on, request that it be enabled.
            // setupChat() will then be called during onActivityResult
            if (!mBluetoothAdapter.isEnabled()) {
                mStatus.setText(R.string.btNotEnabled);
                Log.d(TAG, "onStart: Blueooth adapter detected, but it's not enabled");
            }
        } else {
            mStatus.setText(R.string.noBluetooth);
            Log.d(TAG, "onStart: No blueooth adapter detected, it needs to be present and enabled");
        }

    }

    @Override
    public synchronized void onResume() {
        super.onResume();
        Log.d(TAG, "onResume");

        //map
        mGoogleApiClient.connect();

        locMan = (LocationManager) getSystemService(Context.LOCATION_SERVICE);
        //get last location
        //Location lastLoc = locMan.getLastKnownLocation(LocationManager.NETWORK_PROVIDER);
        //locMan.requestLocationUpdates(LocationManager.NETWORK_PROVIDER,10000,100,loclist); //NOT WORKING
        //locMan.requestLocationUpdates(LocationManager.NETWORK_PROVIDER, 30000, 100, this);

        // Performing this check in onResume() covers the case in which BT was
        // not enabled during onStart(), so we were paused to enable it...
        // onResume() will be called when ACTION_REQUEST_ENABLE activity returns.
        if (mHxmService != null) {
            // Only if the state is STATE_NONE, do we know that we haven't started already
            if (mHxmService.getState() == R.string.HXM_SERVICE_RESTING) {
                // Start the Bluetooth scale services
                mHxmService.start();
            }
        }
    }

    private void setupHrm() {
        Log.d(TAG, "setupScale:");

        // Initialize the service to perform bluetooth connections
        mHxmService = new HxmService(this, mHandler);
    }

    @Override
    public synchronized void onPause() {
        super.onPause();
        Log.e(TAG, "- ON PAUSE -");

        //map
        if (mGoogleApiClient.isConnected()) {
            LocationServices.FusedLocationApi.removeLocationUpdates(mGoogleApiClient, this);
            mGoogleApiClient.disconnect();
        }
    }

    @Override
    public void onStop() {
        super.onStop();
        Log.e(TAG, "-- ON STOP --");
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        // Stop the Bluetooth chat services
        if (mHxmService != null) mHxmService.stop();
        Log.e(TAG, "--- ON DESTROY ---");
    }

    /**
     * Sends a message.
     * @param message  A string of text to send.
     */
    // The Handler that gets information back from the hrm service
    private final Handler mHandler = new Handler() {
        @Override
        public void handleMessage(Message msg) {
            switch (msg.what) {
                case R.string.HXM_SERVICE_MSG_STATE:
                    Log.d(TAG, "handleMessage():  MESSAGE_STATE_CHANGE: " + msg.arg1);
                    switch (msg.arg1) {
                        case R.string.HXM_SERVICE_CONNECTED:
                            if ((mStatus != null) && (mHxMName != null)) {
                                mStatus.setText(R.string.connectedTo);
                                mStatus.append(mHxMName);
                            }
                            break;

                        case R.string.HXM_SERVICE_CONNECTING:
                            mStatus.setText(R.string.connecting);
                            break;

                        case R.string.HXM_SERVICE_RESTING:
                            if (mStatus != null ) {
                                mStatus.setText(R.string.notConnected);
                            }
                            break;
                    }
                    break;

                case R.string.HXM_SERVICE_MSG_READ: {
				/*
				 * MESSAGE_READ will have the byte buffer in tow, we take it, build an instance
				 * of a HrmReading object from the bytes, and then display it into our view
				 */
                    byte[] readBuf = (byte[]) msg.obj;
                    HrmReading hrm = new HrmReading( readBuf );
                    displayHrmReading(hrm);

                    if(isExternalStorageWritable() && isRecording){
                        exportData(hrm); //add location here and to function
                    }
                    break;
                }

                case R.string.HXM_SERVICE_MSG_TOAST:
                    Toast.makeText(getApplicationContext(), msg.getData().getString(null),Toast.LENGTH_SHORT).show();
                    break;
            }
        }
    };


    @Override
    public void onActivityResult(int requestCode, int resultCode, Intent data) {
        Log.d(TAG, "onActivityResult " + requestCode);

        switch(requestCode)
        {

            case 1:
                break;

        }
    }

    /****************************************************************************
     * Some utility functions to control the formatting of HxM fields into the
     * activity's view
     ****************************************************************************/
    private void displayHrmReading(HrmReading h){
        display ( R.id.stx,  h.stx );
        display ( R.id.msgId,  h.msgId );
        display ( R.id.dlc,  h.dlc );
        display ( R.id.firmwareId,   h.firmwareId );
        display ( R.id.firmwareVersion,   h.firmwareVersion );
        display ( R.id.hardwareId,   h.hardWareId );
        display ( R.id.hardwareVersion,   h.hardwareVersion );

        //battery stats
        display ( R.id.batteryChargeIndicator,  h.batteryIndicator );
        if(h.batteryIndicator>50){
            battery.setTextColor(getResources().getColor(R.color.green));
        }else{
            battery.setTextColor(getResources().getColor(R.color.red));
        }
        display ( R.id.heartRate, h.heartRate );
        display ( R.id.heartBeatNumber,  h.heartBeatNumber );
        display ( R.id.hbTimestamp1,   h.hbTime1 );
        display ( R.id.hbTimestamp2,   h.hbTime2 );
        display ( R.id.hbTimestamp3,   h.hbTime3 );
        display ( R.id.hbTimestamp4,   h.hbTime4 );
        display ( R.id.hbTimestamp5,   h.hbTime5 );
        display ( R.id.hbTimestamp6,   h.hbTime6 );
        display ( R.id.hbTimestamp7,   h.hbTime7 );
        display ( R.id.hbTimestamp8,   h.hbTime8 );
        display ( R.id.hbTimestamp9,   h.hbTime9 );
        display ( R.id.hbTimestamp10,   h.hbTime10 );
        display ( R.id.hbTimestamp11,   h.hbTime11 );
        display ( R.id.hbTimestamp12,   h.hbTime12 );
        display ( R.id.hbTimestamp13,   h.hbTime13 );
        display ( R.id.hbTimestamp14,   h.hbTime14 );
        display ( R.id.hbTimestamp15,   h.hbTime15 );
        display ( R.id.reserved1,   h.reserved1 );
        display ( R.id.reserved2,   h.reserved2 );
        display ( R.id.reserved3,   h.reserved3 );
        display ( R.id.distance,   h.distance );
        display ( R.id.speed,   h.speed );
        display ( R.id.strides,  (int)h.strides );
        display ( R.id.reserved4,  h.reserved4 );
        display ( R.id.reserved5,  h.reserved5 );
        display ( R.id.crc,  h.crc );
        display ( R.id.etx,  h.etx );
    }

    /*
     * display a byte value
     */
    private void display  ( int nField, byte d ) {
        String INT_FORMAT = "%x";
        String s = String.format(INT_FORMAT, d);
        display(nField, s);
    }

    /*
     * display an integer value
     */
    private void display  ( int nField, int d ) {
        String INT_FORMAT = "%d";
        String s = String.format(INT_FORMAT, d);
        display( nField, s  );
    }

    /*
     * display a long integer value
     */
    private void display  ( int nField, long d ) {
        String INT_FORMAT = "%d";
        String s = String.format(INT_FORMAT, d);
        display( nField, s  );
    }

    /*
     * display a character string
     */
    private void display ( int nField, CharSequence  str  ) {
        TextView tvw = (TextView) findViewById(nField);
        if ( tvw != null )
            tvw.setText(str);
    }

    @Override
    public void onConnected(Bundle bundle) {
        Location location = LocationServices.FusedLocationApi.getLastLocation(mGoogleApiClient);
        if (location == null) {
            LocationServices.FusedLocationApi.requestLocationUpdates(mGoogleApiClient, mLocationRequest, this);
        } else {
            handleNewLocation(location);
        }
    }

    @Override
    public void onConnectionSuspended(int i) {

    }

    private void handleNewLocation(Location location) {
        Log.d(TAG, location.toString());

        //set current points so they can be used by fragment
        currentLatitude = location.getLatitude();
        currentLongitude = location.getLongitude();
    }

    @Override
    public void onLocationChanged(Location location) {
        handleNewLocation(location);
    }

    @Override
    public void onConnectionFailed(ConnectionResult connectionResult) {

    }

    //more location stuff
    protected synchronized void buildGoogleApiClient() {
        mGoogleApiClient = new GoogleApiClient.Builder(this)
                .addConnectionCallbacks(this)
                .addOnConnectionFailedListener(this)
                .addApi(LocationServices.API)
                .build();
        createLocationRequest();
    }

    protected void createLocationRequest() {
        mLocationRequest = new LocationRequest();

        mLocationRequest = LocationRequest.create()
                .setPriority(LocationRequest.PRIORITY_HIGH_ACCURACY)
                .setInterval(10 * 1000)        // 10 seconds, in milliseconds
                .setFastestInterval(1 * 1000); // 1 seconds, in milliseconds
    }
}
