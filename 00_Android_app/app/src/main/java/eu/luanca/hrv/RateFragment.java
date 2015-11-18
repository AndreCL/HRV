package eu.luanca.hrv;

import android.app.Fragment;
import android.os.Bundle;
import android.os.Environment;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageButton;

import com.google.android.gms.location.LocationRequest;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.PrintWriter;
import java.text.DateFormat;
import java.util.Date;

/**
 * Created by andre_000 on 17-09-2015.
 * Unused!!!!!!!!!!!!!!!!!!!
 */
public class RateFragment extends Fragment {

    ImageButton ok;
    public static final String TAG = MapsActivity.class.getSimpleName();
    private final static int CONNECTION_FAILURE_RESOLUTION_REQUEST = 9000;
    private LocationRequest mLocationRequest;
    String filename = "HRV.txt";


    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        return inflater.inflate(R.layout.fragment_rate, container, false);
    }

    @Override
    public void onActivityCreated(Bundle savedInstanceState) {
        super.onActivityCreated(savedInstanceState);

        /*Report status*/
        ok = (ImageButton)  getView().findViewById(R.id.okButton);
        ok.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {

                //add to location file (change later to add the other stuff)
                if (isExternalStorageWritable() == true) {
                    String currentDateTimeString = DateFormat.getDateTimeInstance().format(new Date());
                    writeToSDFile(currentDateTimeString, ((MapsActivity)getActivity()).currentLatitude, ((MapsActivity)getActivity()).currentLongitude);
                } else {
                    Log.i(TAG, "no external storage?");
                }

                kill();
            }
        });
    }

    //close
    public void kill() {
        getActivity().getFragmentManager().beginTransaction().remove(this).commit();
    }

    /*File Saving*/
    /* Checks if external storage is available for read and write */
    public boolean isExternalStorageWritable() {
        String state = Environment.getExternalStorageState();
        if (Environment.MEDIA_MOUNTED.equals(state)) {
            return true;
        }
        return false;
    }
    private void writeToSDFile(String date, double l1, double l2) {

        // Find the root of the external storage.
        // See http://developer.android.com/guide/topics/data/data-  storage.html#filesExternal
        File root = android.os.Environment.getExternalStorageDirectory();

        // See http://stackoverflow.com/questions/3551821/android-write-to-sd-card-folder
        File dir = new File(root.getAbsolutePath() + "/download");
        dir.mkdirs();
        File file = new File(dir, filename);

        try {
            FileOutputStream f = new FileOutputStream(file, true); //true tells it to append the data
            PrintWriter pw = new PrintWriter(f);
            pw.println(date + "," + l1 + "," + l2);
            pw.flush();
            pw.close();
            f.close();
        } catch (FileNotFoundException e) {
            e.printStackTrace();
            Log.i(TAG, "******* File not found. Did you" +
                    " add a WRITE_EXTERNAL_STORAGE permission to the   manifest?");
        } catch (IOException e) {
            e.printStackTrace();
        }
    }


}