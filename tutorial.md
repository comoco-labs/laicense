# Tutorial

## Step 1: Create a representative token of your dataset

1. Prepare your dataset.

   ```typescript
   datasetUri = "https://raw.githubusercontent.com/comoco-labs/lAIcense/main/dataset/data.csv";
   ```

2. Deploy a `DerivativeToken` contract to represent the dataset collection if not existing.

   ```typescript
   const DerivativeToken = await ethers.getContractFactory("DerivativeToken");
   const datasetCollection = await upgrades.deployProxy(DerivativeToken, [admin, datasetOwner, name, symbol, registry]);
   await datasetCollection.deployed();
   ```

3. Mint your dataset as a token of the contract.

   ```typescript
   await datasetCollection.mint(datasetOwner, datasetTokenId, datasetUri, [], []);
   ```

Refer [here](scripts/1_mint_dataset_token.ts) for the complete code.

## Step 2: Issue an option to license your dataset for model training

1. Deploy a `DerivativeOption` contract.

   ```typescript
   const DerivativeOption = await ethers.getContractFactory("DerivativeOption");
   const datasetDerivativeOption = await upgrades.deployProxy(DerivativeOption, [datasetOwner, ""]);
   await datasetDerivativeOption.deployed();
   ```

2. Mint a token in the contract to represent the option.

   ```typescript
   datasetOptionId = await datasetDerivativeOption.mint(datasetOwner, 1, datasetToken, []);
   ```

3. Bind the option to the dataset token.

   ```typescript
   await datasetCollection.addDerivativeOption(datasetTokenId, [datasetOption]);
   ```

Refer [here](scripts/2_issue_dataset_option.ts) for the complete code.

## Step 3: Acquire the dataset option and train your model

1. Acquire the dataset option for the model.

   ```typescript
   await datasetDerivativeOption.safeTransferFrom(dataSetOwner, modelOwner, datasetOptionId, 1, null);
   ```

Refer [here](scripts/3_acquire_dataset_option.ts) for the complete code.

2. Train over the dataset to produce a model.

   ```python
   for epoch in range(num_epochs):
      running_loss = 0.0

      for batch, (inputs, targets) in enumerate(dataloader):
            outputs = model(inputs)
            loss = criterion(outputs, targets)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
   ```

Refer [here](model/train.py) for the complete code.

## Step 4: Create a representative token of your model

1. Prepare your model.

   ```typescript
   modelUri = "https://raw.githubusercontent.com/comoco-labs/lAIcense/main/model/model.pt";
   ```

2. Deploy a `DerivativeToken` contract to represent the model collection if not existing.

   ```typescript
   const DerivativeToken = await ethers.getContractFactory("DerivativeToken");
   const modelCollection = await upgrades.deployProxy(DerivativeToken, [admin, modelOwner, name, symbol, registry]);
   await modelCollection.deployed();
   ```

3. Authorize the contract to be able to consume the acquired dataset option.

   ```typescript
   await datasetDerivativeOption.setApprovalForAll(modelCollection, true);
   ```

4. Mint your model as a token of the contract derived from the dataset.

   ```typescript
   await modelCollection.mint(modelOwner, modelTokenId, modelUri, [datasetToken], [datasetOption]);
   ```

Refer [here](scripts/4_mint_model_token.ts) for the complete code.

## Step 5: Issue an option to license your model for external applications

1. Deploy a `UtilityOption` contract.

   ```typescript
   const UtilityOption = await ethers.getContractFactory("UtilityOption");
   const modelUtilityOption = await upgrades.deployProxy(UtilityOption, [modelOwner, ""]);
   await modelUtilityOption.deployed();
   ```

2. Mint a token in the contract to represent the option.

   ```typescript
   modelOptionId = await modelUtilityOption.mint(modelOwner, 1, modelToken, []);
   ```

3. Bind the option to the model token.

   ```typescript
   await modelCollection.addUtilityOption(modelTokenId, [modelOption]);
   ```

Refer [here](scripts/5_issue_model_option.ts) for the complete code.

## Step 6: Acquire the model option and validate application usage

1. Acquire the model option for the application.

   ```typescript
   await modelUtilityOption.safeTransferFrom(modelOwner, app, modelOptionId, 1, null);
   ```

2. The model validates the provided option when integrated into the application.

3. The statistics of the model usage, such as the quantities of installation, or the number of inferences made, will be calculated and securely verified on the blockchain, providing transparency and accountability within the system.
