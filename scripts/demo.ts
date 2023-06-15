import { BigNumber, Contract } from 'ethers';
import { ethers, upgrades } from 'hardhat';

// TODO: Remove in future
const REGISTRY_ADDRESS = '0xa73f316A31149230732aCdA4e63706556bE63CC8';

async function mintDatasetToken(): Promise<[Contract, BigNumber]> {
  // Get accounts
  const [admin, datasetOwner] = await ethers.getSigners();

  // Deploy contract
  const datasetName = 'Dataset Collection';
  const datasetSymbol = 'DC';

  const derivativeTokenFactory = await ethers.getContractFactory('DerivativeToken');
  const datasetCollection = await upgrades.deployProxy(derivativeTokenFactory, [admin.address, datasetOwner.address, datasetName, datasetSymbol, REGISTRY_ADDRESS]);
  await datasetCollection.deployed();

  // Mint token
  const datasetTokenId = BigNumber.from(0);
  const datasetUri = 'https://raw.githubusercontent.com/comoco-labs/lAIcense/main/dataset/data.csv';

  await datasetCollection.connect(datasetOwner).mint(datasetOwner.address, datasetTokenId, datasetUri, [], []);

  // Print result
  const datasetToken = { collection: datasetCollection.address, id: datasetTokenId };
  console.log('Dataset token minted at', datasetToken);

  return [datasetCollection, datasetTokenId];
}

async function issueDatasetOption(
  datasetCollection: Contract, datasetTokenId: BigNumber
): Promise<[Contract, BigNumber]> {
  // Get accounts
  const [_admin, datasetOwner] = await ethers.getSigners();

  // Deploy contract
  const derivativeOptionFactory = await ethers.getContractFactory('DerivativeOption');
  const datasetDerivativeOption = await upgrades.deployProxy(derivativeOptionFactory, [datasetOwner.address, '']);
  await datasetDerivativeOption.deployed();

  // Mint token
  const datasetToken = { collection: datasetCollection.address, id: datasetTokenId };
  const datasetOptionId = await datasetDerivativeOption.connect(datasetOwner).callStatic.mint(datasetOwner.address, 1, datasetToken, []);
  await datasetDerivativeOption.connect(datasetOwner).mint(datasetOwner.address, 1, datasetToken, []);

  // Bind option
  const datasetOption = { collection: datasetDerivativeOption.address, id: datasetOptionId };
  await datasetCollection.connect(datasetOwner).addDerivativeOption(datasetTokenId, [datasetOption]);

  // Print result
  console.log('Dataset option issued at', datasetOption);

  return [datasetDerivativeOption, datasetOptionId];
}

async function acquireDatasetOption(
  datasetDerivativeOption: Contract, datasetOptionId: BigNumber
) {
  // Get accounts
  const [_admin, datasetOwner, modelOwner] = await ethers.getSigners();

  // Acquire option
  await datasetDerivativeOption.connect(datasetOwner).safeTransferFrom(datasetOwner.address, modelOwner.address, datasetOptionId, 1, []);

  // Print result
  console.log('Dataset option acquired by model owner');
}

async function mintModelToken(
  datasetCollection: Contract, datasetTokenId: BigNumber, datasetDerivativeOption: Contract, datasetOptionId: BigNumber
): Promise<[Contract, BigNumber]> {
  // Get accounts
  const [admin, _datasetOwner, modelOwner] = await ethers.getSigners();

  // Deploy contract
  const modelName = 'Model Collection';
  const modelSymbol = 'MC';

  const derivativeTokenFactory = await ethers.getContractFactory('DerivativeToken');
  const modelCollection = await upgrades.deployProxy(derivativeTokenFactory, [admin.address, modelOwner.address, modelName, modelSymbol, REGISTRY_ADDRESS]);
  await modelCollection.deployed();

  // Authorize option
  await datasetDerivativeOption.connect(modelOwner).setApprovalForAll(modelCollection.address, true);

  // Mint token
  const modelTokenId = BigNumber.from(0);
  const modelUri = 'https://raw.githubusercontent.com/comoco-labs/lAIcense/main/model/model.pt';

  const datasetToken = { collection: datasetCollection.address, id: datasetTokenId };
  const datasetOption = { collection: datasetDerivativeOption.address, id: datasetOptionId };
  await modelCollection.connect(modelOwner).mint(modelOwner.address, modelTokenId, modelUri, [datasetToken], [datasetOption]);

  // Print result
  const modelToken = { collection: modelCollection.address, id: modelTokenId };
  console.log('Model token minted at', modelToken);

  return [modelCollection, modelTokenId];
}

async function issueModelOption(
  modelCollection: Contract, modelTokenId: BigNumber
): Promise<[Contract, BigNumber]> {
  // Get accounts
  const [_admin, _datasetOwner, modelOwner] = await ethers.getSigners();

  // Deploy contract
  const utilityOptionFactory = await ethers.getContractFactory('UtilityOption');
  const modelUtilityOption = await upgrades.deployProxy(utilityOptionFactory, [modelOwner.address, '']);
  await modelUtilityOption.deployed();

  // Mint token
  const modelToken = { collection: modelCollection.address, id: modelTokenId };
  const modelOptionId = await modelUtilityOption.connect(modelOwner).callStatic.mint(modelOwner.address, 1, modelToken, []);
  await modelUtilityOption.connect(modelOwner).mint(modelOwner.address, 1, modelToken, []);

  // Bind option
  const modelOption = { collection: modelUtilityOption.address, id: modelOptionId };
  await modelCollection.connect(modelOwner).addUtilityOption(modelTokenId, [modelOption]);

  // Print result
  console.log('Model option issued at', modelOption);

  return [modelUtilityOption, modelOptionId];
}

async function acquireModelOption(
  modelUtilityOption: Contract, modelOptionId: BigNumber
) {
  // Get accounts
  const [_admin, _datasetOwner, modelOwner, app] = await ethers.getSigners();

  // Acquire option
  await modelUtilityOption.connect(modelOwner).safeTransferFrom(modelOwner.address, app.address, modelOptionId, 1, []);

  // Print result
  console.log('Model option acquired by application');
}

async function main() {
  const [datasetCollection, datasetTokenId] = await mintDatasetToken();
  const [datasetDerivativeOption, datasetOptionId] = await issueDatasetOption(datasetCollection, datasetTokenId);
  await acquireDatasetOption(datasetDerivativeOption, datasetOptionId);
  const [modelCollection, modelTokenId] = await mintModelToken(datasetCollection, datasetTokenId, datasetDerivativeOption, datasetOptionId);
  const [modelUtilityOption, modelOptionId] = await issueModelOption(modelCollection, modelTokenId);
  await acquireModelOption(modelUtilityOption, modelOptionId);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
