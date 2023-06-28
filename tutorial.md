# Tutorial

## Step 1: Create a representative token of your dataset

1. Prepare your dataset.

   ```typescript
   const datasetUri = 'https://raw.githubusercontent.com/comoco-labs/lAIcense/main/dataset/';
   ```

2. Deploy a `DerivativeToken` contract to represent the dataset collection if not existing.

   ```typescript
   const derivativeTokenFactory = await ethers.getContractFactory('DerivativeToken');
   const datasetCollection = await upgrades.deployProxy(derivativeTokenFactory, [admin.address, datasetOwner.address, datasetName, datasetSymbol, REGISTRY_ADDRESS]);
   await datasetCollection.deployed();
   ```

3. Mint your dataset as a token of the contract.

   ```typescript
   await datasetCollection.connect(datasetOwner).mint(datasetOwner.address, datasetTokenId, datasetUri, [], []);
   ```

Refer [here](scripts/demo.ts#L7) for the complete code.

## Step 2: Issue an option to license your dataset for model training

1. Deploy a `DerivativeOption` contract.

   ```typescript
   const DerivativeOption = await ethers.getContractFactory('DerivativeOption');
   const datasetDerivativeOption = await upgrades.deployProxy(derivativeOptionFactory, [datasetOwner.address, '']);
   await datasetDerivativeOption.deployed();
   ```

2. Mint a token in the contract to represent the option.

   ```typescript
   const datasetOptionId = await datasetDerivativeOption.connect(datasetOwner).mint(datasetOwner.address, 1, datasetToken, []);
   ```

3. Bind the option to the dataset token.

   ```typescript
   await datasetCollection.connect(datasetOwner).addDerivativeOption(datasetTokenId, [datasetOption]);
   ```

Refer [here](scripts/demo.ts#L32) for the complete code.

## Step 3: Acquire the dataset option and train your model

1. Acquire the dataset option for the model.

   ```typescript
   await datasetDerivativeOption.connect(datasetOwner).safeTransferFrom(datasetOwner.address, modelOwner.address, datasetOptionId, 1, []);
   ```

Refer [here](scripts/demo.ts#L58) for the complete code.

2. Train over the dataset to produce a model.

   ```python
   model.fit(x_train, y_train, batch_size=batch_size, epochs=epochs, validation_data=(x_val, y_val))
   ```

Refer [here](scripts/train.py) for the complete code.

## Step 4: Create a representative token of your model

1. Prepare your model.

   ```typescript
   const modelUri = 'https://raw.githubusercontent.com/comoco-labs/lAIcense/main/model/model.tflite';
   ```

2. Deploy a `DerivativeToken` contract to represent the model collection if not existing.

   ```typescript
   const DerivativeToken = await ethers.getContractFactory('DerivativeToken');
   const modelCollection = await upgrades.deployProxy(derivativeTokenFactory, [admin.address, modelOwner.address, modelName, modelSymbol, REGISTRY_ADDRESS]);
   await modelCollection.deployed();
   ```

3. Authorize the contract to be able to consume the acquired dataset option.

   ```typescript
   await datasetDerivativeOption.connect(modelOwner).setApprovalForAll(modelCollection.address, true);
   ```

4. Mint your model as a token of the contract derived from the dataset.

   ```typescript
   await modelCollection.connect(modelOwner).mint(modelOwner.address, modelTokenId, modelUri, [datasetToken], [datasetOption]);
   ```

Refer [here](scripts/demo.ts#L71) for the complete code.

## Step 5: Issue an option to license your model for external applications

1. Deploy a `UtilityOption` contract.

   ```typescript
   const UtilityOption = await ethers.getContractFactory('UtilityOption');
   const modelUtilityOption = await upgrades.deployProxy(utilityOptionFactory, [modelOwner.address, '']);
   await modelUtilityOption.deployed();
   ```

2. Mint a token in the contract to represent the option.

   ```typescript
   const modelOptionId = await modelUtilityOption.connect(modelOwner).mint(modelOwner.address, 1, modelToken, []);
   ```

3. Bind the option to the model token.

   ```typescript
   await modelCollection.connect(modelOwner).addUtilityOption(modelTokenId, [modelOption]);
   ```

Refer [here](scripts/demo.ts#L103) for the complete code.

## Step 6: Acquire the model option and validate application usage

1. Acquire the model option for the application.

   ```typescript
   await modelUtilityOption.connect(modelOwner).safeTransferFrom(modelOwner.address, app.address, modelOptionId, 1, []);
   ```

2. The model validates the provided option when integrated into the application.

3. The statistics of the model usage, such as the quantities of installation, or the number of inferences made, will be calculated and securely verified on the blockchain, providing transparency and accountability within the system.

Refer [here](scripts/demo.ts#L129) for the complete code.
