import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Dimension;
import java.awt.Graphics2D;
import java.awt.image.BufferedImage;
import java.io.File;

import javax.imageio.ImageIO;
import javax.swing.BorderFactory;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.SwingUtilities;

import org.apache.jmeter.reporters.ResultCollector;
import org.apache.jmeter.save.CSVSaveService;
import org.apache.jmeter.util.JMeterUtils;
import org.apache.jmeter.visualizers.StatVisualizer;
import org.apache.jmeter.visualizers.SummaryReport;
import org.apache.jmeter.visualizers.ViewResultsFullVisualizer;
import org.apache.jmeter.visualizers.gui.AbstractVisualizer;

/**
 * Render a saved JTL with the real JMeter report components and save a PNG.
 *
 * Usage:
 *   java JtlScreenshot <summary|aggregate|tree> <results.jtl> <out.png> "<header>"
 *
 * This is not a mock: SummaryReport, StatVisualizer and
 * ViewResultsFullVisualizer are the exact classes JMeter uses for the
 * Summary Report, Aggregate Report and View Results Tree listeners.
 */
public final class JtlScreenshot {

    private static void selectFirstTreeRow(java.awt.Component root) {
        if (root instanceof javax.swing.JTree) {
            javax.swing.JTree tree = (javax.swing.JTree) root;
            if (tree.getRowCount() > 0) {
                tree.setSelectionInterval(0, 0);
                tree.scrollRowToVisible(0);
            }
            return;
        }
        if (root instanceof java.awt.Container) {
            for (java.awt.Component child : ((java.awt.Container) root).getComponents()) {
                selectFirstTreeRow(child);
            }
        }
    }

    public static void main(String[] args) throws Exception {
        if (args.length < 4) {
            System.err.println("usage: JtlScreenshot <summary|aggregate|tree> <jtl> <png> <header>");
            System.exit(2);
        }
        String kind = args[0];
        File jtl = new File(args[1]);
        File out = new File(args[2]);
        String header = args[3];

        String home = System.getenv("JMETER_HOME");
        if (home == null) {
            home = "C:\\HCMUS\\hk7\\Testing\\apache-jmeter-5.6.3";
        }
        JMeterUtils.setJMeterHome(home);
        JMeterUtils.loadJMeterProperties(new File(home, "bin/jmeter.properties").getAbsolutePath());
        JMeterUtils.initLocale();

        final AbstractVisualizer view;
        switch (kind) {
            case "summary":
                view = new SummaryReport();
                break;
            case "aggregate":
                view = new StatVisualizer();
                break;
            case "tree":
                view = new ViewResultsFullVisualizer();
                break;
            default:
                throw new IllegalArgumentException("unknown view: " + kind);
        }

        ResultCollector collector = new ResultCollector();
        collector.setListener(view);
        System.out.println("loading " + jtl.getAbsolutePath());
        CSVSaveService.processSamples(jtl.getAbsolutePath(), view, collector);
        System.out.println("parsed " + jtl.getName());

        final JFrame frame = new JFrame(header);
        JPanel root = new JPanel(new BorderLayout());
        root.setBackground(Color.WHITE);
        JLabel title = new JLabel(header);
        title.setBorder(BorderFactory.createEmptyBorder(6, 10, 6, 10));
        title.setOpaque(true);
        title.setBackground(new Color(245, 245, 245));
        root.add(title, BorderLayout.NORTH);
        root.add(view, BorderLayout.CENTER);
        frame.setContentPane(root);
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setSize(new Dimension(1500, 900));
        frame.setVisible(true);

        // Select the first row so the right-hand pane shows a real sample.
        selectFirstTreeRow(view);

        // Let Swing finish layout and let the table/tree models settle.
        Thread.sleep(2500);
        SwingUtilities.invokeAndWait(new Runnable() {
            @Override
            public void run() {
                try {
                    BufferedImage img = new BufferedImage(
                            frame.getContentPane().getWidth(),
                            frame.getContentPane().getHeight(),
                            BufferedImage.TYPE_INT_RGB);
                    Graphics2D g = img.createGraphics();
                    frame.getContentPane().paint(g);
                    g.dispose();
                    ImageIO.write(img, "png", out);
                } catch (Exception exc) {
                    throw new RuntimeException(exc);
                }
            }
        });
        frame.dispose();
        System.out.println("wrote " + out.getAbsolutePath());
        System.out.flush();
        System.exit(0);
    }
}
