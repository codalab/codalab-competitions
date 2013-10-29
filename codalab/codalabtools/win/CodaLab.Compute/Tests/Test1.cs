using System;
using System.Collections.Generic;
using System.Configuration;
using System.IO;
using System.Net;
using System.Text;
using System.Runtime.Serialization.Json;

using Microsoft.FSharp.Core;
using Microsoft.VisualStudio.TestTools.UnitTesting;
using Microsoft.WindowsAzure.Storage;
using Microsoft.WindowsAzure.Storage.Blob;

using CodaLab.Bundles;
using CodaLab.Compute;
using CodaLab.Compute.Azure;


namespace Tests
{
    [TestClass]
    public class Test1
    {
        public const string AzureConnectionStringKey = "AzureStorageConnectionString";
        public const string AzureContainerName = "AzureContainerName";

        public string[] inputBundleIds = new string[] { 
            "competition1/program.zip",
            "competition1/reference.zip",
            "competition1/submission1/run.txt",
            "competition1/submission1/input.txt",
            "competition1/submission1/answer.zip"
        };

        public string[] inputBundlePaths = new string[] { 
            Path.Combine("TestData", "competition1", "program.zip"),
            Path.Combine("TestData", "competition1", "reference.zip"),
            Path.Combine("TestData", "competition1", "submission1", "run.txt"),
            Path.Combine("TestData", "competition1", "submission1", "input.txt"),
            Path.Combine("TestData", "competition1", "submission1", "answer.zip")
        };

        public string[] outputBundleIds = new string[] { 
            "competition1/submission1/run/output.zip",
            "competition1/submission1/run/stdout.txt",
            "competition1/submission1/run/stderr.txt",
        };

        private static TestContext _context;

        private static string TestDataParentPath {
            get {
                string path = Environment.CurrentDirectory;
                if (Directory.Exists(Path.Combine(path, "TestData")))
                {
                    return path;
                }
                return Directory.GetParent(path).Parent.Parent.FullName;
            }
        }

        [AssemblyInitialize]
        public static void Setup(TestContext context)
        {
            _context = context;
        }

        [TestMethod(), TestCategory("Local")]
        public void CreateLocalReferenceTest()
        {
            bool[] expected = new bool[] { true, true, false, false, true };
            for (int i = 0; i < inputBundleIds.Length; i++)
            {
                string bundlePath = Path.Combine(Test1.TestDataParentPath, inputBundlePaths[i]);
                Assert.IsTrue(File.Exists(bundlePath));
                bool isZip = String.Compare(".zip", Path.GetExtension(bundlePath)) == 0;
                var localRef = LocalBundleReference.Create(bundlePath);
                Assert.IsNotNull(localRef);
                Assert.AreEqual(expected[i], isZip);
                Assert.AreEqual(isZip, localRef.IsZipBundle);
                Assert.AreNotEqual(isZip, localRef.IsMetadataOnlyBundle);
            }
        }

        [TestMethod(), TestCategory("Local")]
        public void RunLocalTest()
        {
            LocalBundleStore localStore = new LocalBundleStore();
            for (int i = 0; i < inputBundleIds.Length; i++)
            {
                string bundleId = inputBundleIds[i];
                Assert.IsFalse(localStore.HasReference(bundleId));
                string bundlePath = Path.Combine(Test1.TestDataParentPath, inputBundlePaths[i]);
                localStore.PutReference(bundleId, bundlePath);
                Assert.IsTrue(localStore.HasReference(bundleId));
                var bundleRef = localStore.GetReference(bundleId);
                Assert.IsNotNull(bundleRef.Value);
            }

            BundleStore store = localStore.GetStore();
            Assert.IsNotNull(store);

            string bundleSvcPath = Path.Combine(_context.TestRunDirectory, @"RunLocalTestBundles");
            Directory.CreateDirectory(bundleSvcPath);
            BundleService bundleSvc = new BundleService(store, bundleSvcPath, false);

            var runId = inputBundleIds[2];
            var outputId = runId.Substring(0, runId.Length - Path.GetExtension(runId).Length) + @"/output.zip";
            Assert.AreEqual(outputId, outputBundleIds[0]);
            Assert.IsFalse(bundleSvc.Has(outputId));

            Run.executeIt(bundleSvc, runId, LocalDiagnostics.get());

            Assert.IsTrue(bundleSvc.Has(outputId));
            Assert.IsTrue(localStore.HasReference(outputId));
            var outputRef = localStore.GetReference(outputId);
            Assert.IsTrue(outputRef.Value.IsZipBundle);

            var outputBundle = bundleSvc.Get(outputId);
            Assert.IsNotNull(outputBundle);
            var scorepath = Path.Combine(outputBundle.AbsolutePath, @"scores.txt");
            Assert.IsTrue(File.Exists(scorepath));
            string[] lines = File.ReadAllLines(scorepath);
            Assert.AreEqual(1, lines.Length);
            string[] line1Parts = lines[0].Split(':');
            Assert.AreEqual(2, line1Parts.Length);
            Assert.AreEqual("Difference", line1Parts[0].Trim());
            Assert.AreEqual("0.041593", line1Parts[1].Trim());

            var stdoutPath = Path.Combine(bundleSvcPath, @"competition1\submission1\run\stdout.txt");
            Assert.IsTrue(File.Exists(scorepath));
            var stderrPath = Path.Combine(bundleSvcPath, @"competition1\submission1\run\stderr.txt");
            Assert.IsTrue(File.Exists(scorepath));
        }

        [TestMethod(), TestCategory("Local")]
        public void RunAzureTest()
        {
            var connectionInfo = ConfigurationManager.AppSettings[AzureConnectionStringKey];
            var containerName = ConfigurationManager.AppSettings[AzureContainerName];
            var account = CloudStorageAccount.Parse(ConfigurationManager.AppSettings[AzureConnectionStringKey]);
            var container = account.CreateCloudBlobClient().GetContainerReference(containerName);
            if (connectionInfo.StartsWith("UseDevelopmentStorage=true"))
            {
                container.CreateIfNotExists();
            }
            Assert.IsTrue(container.Exists());

            // Clean the container
            var bundleIds = new List<string>();
            bundleIds.AddRange(inputBundleIds);
            bundleIds.AddRange(outputBundleIds);
            DeleteBlobsIfExists(container, bundleIds);

            string azureStorePath = Path.Combine(_context.TestRunDirectory, @"RunAzureTestBlobs");
            Directory.CreateDirectory(azureStorePath);
            AzureBundleStore azureStore = new AzureBundleStore(container, azureStorePath);
            for (int i = 0; i < inputBundleIds.Length; i++)
            {
                string bundleId = inputBundleIds[i];
                Assert.IsFalse(azureStore.HasReference(bundleId));
                string bundlePath = Path.Combine(Test1.TestDataParentPath, inputBundlePaths[i]);
                azureStore.PutReference(bundleId, bundlePath);
                Assert.IsTrue(azureStore.HasReference(bundleId));
                var bundleRef = azureStore.GetReference(bundleId);
                Assert.IsNotNull(bundleRef.Value);
            }

            BundleStore store = azureStore.GetStore();
            Assert.IsNotNull(store);

            string bundleSvcPath = Path.Combine(_context.TestRunDirectory, @"RunAzureTestBundles");
            Directory.CreateDirectory(bundleSvcPath);
            BundleService bundleSvc = new BundleService(store, bundleSvcPath, true);

            var runId = inputBundleIds[2];
            var outputId = outputBundleIds[0];
            Assert.IsFalse(bundleSvc.Has(outputId));

            Run.executeIt(bundleSvc, runId, AzureDiagnostics.get(container));

            Assert.IsTrue(bundleSvc.Has(outputId));
            Assert.IsTrue(azureStore.HasReference(outputId));
            var outputRef = azureStore.GetReference(outputId);
            Assert.IsTrue(outputRef.Value.IsZipBundle);
            var blobOutput = container.GetBlockBlobReference(outputId);
            Assert.IsTrue(blobOutput.Exists());

            var outputBundle = bundleSvc.Get(outputId);
            Assert.IsNotNull(outputBundle);
            var scorepath = Path.Combine(outputBundle.AbsolutePath, @"scores.txt");
            Assert.IsTrue(File.Exists(scorepath));
            string[] lines = File.ReadAllLines(scorepath);
            Assert.AreEqual(1, lines.Length);
            string[] line1Parts = lines[0].Split(':');
            Assert.AreEqual(2, line1Parts.Length);
            Assert.AreEqual("Difference", line1Parts[0].Trim());
            Assert.AreEqual("0.041593", line1Parts[1].Trim());

            var stdoutId = outputBundleIds[1];
            var blobStdout = container.GetBlockBlobReference(stdoutId);
            Assert.IsTrue(blobStdout.Exists());
            var stderrId = outputBundleIds[2];
            var blobStderr = container.GetBlockBlobReference(stderrId);
            Assert.IsFalse(blobStderr.Exists()); // does not exist because nothing was written to std error

            DeleteBlobsIfExists(container, bundleIds);
        }

        private static void DeleteBlobsIfExists(CloudBlobContainer container, IEnumerable<string> blobNames)
        {
            foreach (var blobName in blobNames)
            {
                var blob = container.GetBlockBlobReference(blobName);
                blob.DeleteIfExists();
            }
            foreach (var blobName in blobNames)
            {
                var blob = container.GetBlockBlobReference(blobName);
                Assert.IsFalse(blob.Exists());
            }
        }
    }
}
