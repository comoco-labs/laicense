import { Contract } from "ethers";
import { ethers } from "hardhat";

const DEAR_COIN_ADDRESS = "0x2Bad2FD9cD88387542B1A7d0a87A1010f6f336F5";
const DATA_COLLECTION_ADDRESS = "0x5a7dE6bAb521Df2c22d4b7b4D8c678Efd7B3F7a6";
const DATASET_COLLECTION_ADDRESS = "0xb7f967952A3AF46Df78971a9cB9a0dc22D060a45";
const MODEL_COLLECTION_ADDRESS = "0x55e7B44Ba036BBa781ACb5a8EcC3ebfb68140A57";

async function setupContracts(owner: ethers.Signer): Promise<[Contract, Contract, Contract, Contract]> {
  const dearCoin = await ethers.getContractAt("DearCoin", DEAR_COIN_ADDRESS, owner);
  const dataCollection = await ethers.getContractAt("DerivativeToken", DATA_COLLECTION_ADDRESS, owner);
  const datasetCollection = await ethers.getContractAt("DerivativeToken", DATASET_COLLECTION_ADDRESS, owner);
  const modelCollection = await ethers.getContractAt("DerivativeToken", MODEL_COLLECTION_ADDRESS, owner);
  return [dearCoin, dataCollection, datasetCollection, modelCollection];
}

async function createData(dataCollection: Contract, userA: ethers.Signer, userB: ethers.Signer) {
  await dataCollection.mint(userA.address, 0, "https://3dwarehouse.sketchup.com/model/371a609f050b4ed3f6497dc58a9a6f8a/SR-71-Blackbird", []);
  await dataCollection.mint(userA.address, 1, "https://3dwarehouse.sketchup.com/model/dd9ece07d4bc696c2bafe808edd44356/x-wing", []);
  await dataCollection.mint(userB.address, 2, "https://3dwarehouse.sketchup.com/model/bcf0b18a19bce6d91ad107790a9e2d51/Hummer-H1-SUT", []);
  await dataCollection.mint(userB.address, 3, "https://3dwarehouse.sketchup.com/model/5876e90c8f0b15e112ed57dd1bc82aa3/Alfa-Romeo-156", []);
  await dataCollection.mint(userB.address, 4, "https://3dwarehouse.sketchup.com/model/402d1624e1c28422383a5be3771c595c/1957-Chevrolet-Bel-Air", []);
}

async function issueCredits(dearCoin: Contract, userA: ethers.Signer, userB: ethers.Signer) {
  await dearCoin.mint(userA.address, 3);
  await dearCoin.mint(userB.address, 7);
}

async function createDatasets(datasetCollection: Contract, owner: ethers.Signer) {
  await datasetCollection.mint(owner.address, 0, "https://raw.githubusercontent.com/comoco-labs/laicense/dev/dataset/0.json", []);
  await datasetCollection.mint(owner.address, 1, "https://raw.githubusercontent.com/comoco-labs/laicense/dev/dataset/1.json", []);
}

async function subscribeDataset(datasetCollection: Contract, userC: ethers.Signer) {
  await datasetCollection.setUser(1, userC.address, 1704096000);
}

async function publicizeModel(modelCollection: Contract, userC: ethers.Signer) {
  await modelCollection.mint(userC.address, 0, "https://raw.githubusercontent.com/comoco-labs/laicense/dev/model/model.tflite", [{collection: DATASET_COLLECTION_ADDRESS, id: 1}]);
}

async function main() {
  const [owner, userA, userB, userC] = await ethers.getSigners();
  const [dearCoin, dataCollection, datasetCollection, modelCollection] = await setupContracts(owner);
  await createData(dataCollection, userA, userB);
  await issueCredits(dearCoin, userA, userB);
  await createDatasets(datasetCollection, owner);
  await subscribeDataset(datasetCollection, userC);
  await publicizeModel(modelCollection, userC);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
