import pandas
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator


class BioprocessMonitor:
    def __init__(self, filepath, ph_lims, temperature_lims):
        """
        Utility class used to monitor bioprocesses by
        generating dashboards and summaries.

        Parameters
        ----------
        filepath : str
            Input CSV dataset path.
        ph_lims : tuple[float, float]
            Lower and upper acceptable pH limits.
        temperature_lims : tuple[float, float]
            Lower and upper acceptable temperature limits.
        """
        self.filepath = filepath
        self.ph_lower=ph_lims[0]
        self.ph_upper=ph_lims[1]
        self.temp_lower=temperature_lims[0]
        self.temp_upper=temperature_lims[1]

    def extract_batch(self, batch_id):
        """
        Extracts data corresponding to a single batch.

        Parameters
        ----------
        batch_id : int
            Batch identifier.

        Returns
        -------
        pandas.DataFrame
            DataFrame containing only rows associated with
            the requested batch.
        """

        df = pandas.read_csv(self.filepath)
        df_batch = df[df["batch_id"] == batch_id]
        return df_batch


    def optimal_ph_mask(self, df_batch):
        """
        Determines whether each pH measurement falls within
        the acceptable operating range.

        Parameters
        ----------
        df_batch : pandas.DataFrame
            Batch-specific DataFrame.

        Returns
        -------
        array-like of bool
            A mask whereby True indicates that the measurement
            is within the acceptable operating range.
        """

        mask_ph_high =df_batch.loc[:,"pH"]<=self.ph_upper
        mask_ph_low =df_batch.loc[:,"pH"]>=self.ph_lower
        mask_ph=mask_ph_high*mask_ph_low
        return mask_ph
    def optimal_temperature_mask(self, df_batch):
        """
        Determines whether each temperature measurement falls
        within the acceptable operating range.

        Parameters
        ----------
        df_batch : pandas.DataFrame
            Batch-specific DataFrame.

        Returns
        -------
        array-like of bool
            A mask whereby True indicates that the measurement
            is within the acceptable operating range.
        """
        mask_temp_high = df_batch.loc[:, "temperature_C"] <= self.temp_upper
        mask_temp_low = df_batch.loc[:, "temperature_C"] >= self.temp_lower
        mask_temp = mask_temp_high * mask_temp_low
        return mask_temp
    def get_n_batches(self):
        """
        Determines the number of unique batches present
        in the dataset.

        Returns
        -------
        int
            Total number of distinct batch identifiers.
        """

        df=pandas.read_csv(self.filepath)
        n=len(np.unique(df["batch_id"]))
        return n
    def export_dashboard(self, batch_id, filepath):
        """
        Creates and saves a dashboard figure for a single batch.

        Parameters
        ----------
        batch_id : int
            Batch identifier.
        filepath : str
            Output PNG image path.

        Dashboard Requirements
        ----------------------
        Create a 2 × 2 figure containing:

        Top-Left
            Glucose, biomass, and product concentrations versus time.
            - A different color and marker should be used for each substance.

        Top-Right
            Temperature versus time.
            - Measurements within the acceptable temperature range
              should be displayed as green circles.
            - Measurements outside the acceptable temperature range
              should be displayed as red X markers.

        Bottom-Left
            pH versus time.
            - Measurements within the acceptable pH range
              should be displayed as green circles.
            - Measurements outside the acceptable pH range
              should be displayed as red X markers.

        Bottom-Right
            Dissolved oxygen versus time.

        Additional Requirements
        -----------------------
        - Use scatter plots.
        - Add x-axis and y-axis labels.
        - Add legends where appropriate.
        - Apply consistent formatting across all subplots unless
          indicated otherwise.
        - Apply a tick spacing of 6 h on the x-axis for all subplots.
        - Save the figure to the provided filepath.
        - Close the figure after saving.
        """
        df=self.extract_batch(batch_id)
        colours = ["tab:blue", "tab:orange", "tab:green", "tab:red", "tab:purple"]
        markers = ["o", "x", "^"]
        fig, ax = plt.subplots(2,2)
        ph_mask=self.optimal_ph_mask(df)
        temp_mask=self.optimal_temperature_mask(df)

        ax[0,0].scatter(df["time_h"], df["C_glucose_g_L^-1"],color=colours[0], marker=markers[0],label="glucose",s=10)
        ax[0,0].scatter(df["time_h"], df["C_biomass_g_L^-1"],color=colours[1], marker=markers[1],label="biomass",s=10)
        ax[0,0].scatter(df["time_h"], df["C_product_g_L^-1"],color=colours[2], marker=markers[2],label="product",s=10)

        ax[0,1].scatter(df["time_h"][temp_mask], df["temperature_C"][temp_mask],color=colours[2], marker=markers[0],label="temp in range",s=10)
        ax[0,1].scatter(df["time_h"][~temp_mask], df["temperature_C"][~temp_mask],color=colours[3], marker=markers[1],label="temp out of range",s=10)

        ax[1,0].scatter(df["time_h"][ph_mask], df["pH"][ph_mask], color=colours[2],marker=markers[0],label="pH in range",s=5)
        ax[1,0].scatter(df["time_h"][~ph_mask], df["pH"][~ph_mask], color=colours[3],marker=markers[1],label = "pH out of range",s=10)

        ax[1,1].scatter(df["time_h"], df["DO_percent"],color=colours[0], marker=markers[0],s=10)

        ax[0,0].legend()
        ax[0,1].legend()
        ax[1,0].legend()



        ax[0,0].set_ylabel("Concentration (g/L)")
        ax[0,1].set_ylabel("Temperature (C)")
        ax[1,0].set_ylabel("pH")
        ax[1,1].set_ylabel("% Dissolved oxygen")

        for ax in np.ravel(ax):
            ax.xaxis.set_major_locator(MultipleLocator(6))
            ax.set_xlabel("Time (h)")

        fig.tight_layout()
        fig.savefig(filepath)
        plt.close(fig)

    def export_summary(self, filepath):
        """
        Generates a batch summary table and exports it to a CSV file.

        Parameters
        ----------
        filepath : str
            Output CSV table path.

        Summary Table Columns
        ---------------------
        batch_id
            Batch identifier.

        ph_optimal_percent
            Percentage of measurements in a batch within the
            acceptable pH range, rounded to 2 decimal places.

        temperature_optimal_percent
            Percentage of measurements in a batch within the
            acceptable temperature range, rounded to 2 decimal places.

        C_product_g_L^-1_final
            Final product concentration for the batch.
        """
        pandas.set_option('display.max_rows', 500)
        pandas.set_option('display.max_columns', 500)
        pandas.set_option('display.width', 1000)
        records=[]
        column_names=["Batch ID", "pH optimal percentage","temperature optimal percentage", "final product concentration g/L"]
        for batch_id in range(1, self.get_n_batches()+1):
            df_batch = self.extract_batch(batch_id)
            ph_in=0
            ph_out=0
            ph_mask=self.optimal_ph_mask(df_batch)
            for ph_value in ph_mask:
                if ph_value:
                    ph_in+=1
                else:
                    ph_out+=1
            ph_optimal_percent=round((ph_in/(ph_out+ph_in))*100,2)
            temp_in=0
            temp_out=0
            temp_mask=self.optimal_temperature_mask(df_batch)
            for temp_value in temp_mask:
                if temp_value:
                    temp_in+=1
                else:
                    temp_out+=1
            temp_optimal_percent=round((temp_in/(temp_out+temp_in))*100,2)
            final_conc=df_batch["C_product_g_L^-1"].iloc[-1]
            record=(batch_id, ph_optimal_percent, temp_optimal_percent, final_conc)
            records.append(record)
        df_export=pandas.DataFrame(records,columns=column_names)
        df_export.to_csv(filepath, index=False)





