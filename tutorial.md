# Tutorial

## Preparation: Contract Deployment

1. We chose Polygon's Mumbai Testnet as our demo environment. Three ERC721 contracts (`DerivativeToken.sol`) and one ERC20 contract (`DearCoin.sol`) have been deployed:

   ```typescript
   const DEAR_COIN_ADDRESS = "0x2Bad2FD9cD88387542B1A7d0a87A1010f6f336F5";
   const DATA_COLLECTION_ADDRESS = "0x5a7dE6bAb521Df2c22d4b7b4D8c678Efd7B3F7a6";
   const DATASET_COLLECTION_ADDRESS = "0xb7f967952A3AF46Df78971a9cB9a0dc22D060a45";
   const MODEL_COLLECTION_ADDRESS = "0x55e7B44Ba036BBa781ACb5a8EcC3ebfb68140A57";
   ```

2. For the following steps, we would use `Contract` objects derived from those addresses:

    ```typescript
   const dearCoin = await ethers.getContractAt("DerivativeToken", DEAR_COIN_ADDRESS);
   const dataCollection = await ethers.getContractAt("DerivativeToken", DATA_COLLECTION_ADDRESS);
   const datasetCollection = await ethers.getContractAt("DerivativeToken", DATASET_COLLECTION_ADDRESS);
   const modelCollection = await ethers.getContractAt("DerivativeToken", MODEL_COLLECTION_ADDRESS);
   ```

3. For the demo purpose, we would create three different users. The first two users are both data creators, and the third user is the model trainer who consumes the dataset:

   ```typescript
   const [_, userA, userB, userC] = await ethers.getSigners();
   ```

## Step 1: Data Creation

1. In this demo, we will use a subset of data from `ShapeNet` dataset as an example. Specifically, User A will upload two airplane 3D models, and User B will upload three car 3D models:

   ```typescript
   await dataCollection.mint(userA.address, 0, "https://3dwarehouse.sketchup.com/model/371a609f050b4ed3f6497dc58a9a6f8a/SR-71-Blackbird", []);
   await dataCollection.mint(userA.address, 1, "https://3dwarehouse.sketchup.com/model/dd9ece07d4bc696c2bafe808edd44356/x-wing", []);
   await dataCollection.mint(userB.address, 2, "https://3dwarehouse.sketchup.com/model/bcf0b18a19bce6d91ad107790a9e2d51/Hummer-H1-SUT", []);
   await dataCollection.mint(userB.address, 3, "https://3dwarehouse.sketchup.com/model/5876e90c8f0b15e112ed57dd1bc82aa3/Alfa-Romeo-156", []);
   await dataCollection.mint(userB.address, 4, "https://3dwarehouse.sketchup.com/model/402d1624e1c28422383a5be3771c595c/1957-Chevrolet-Bel-Air", []);
   ```

2. The minted data IDs range from 0 to 4. We can verify the data ownership from the contract:

   ```typescript
   expect(await dataCollection.ownerOf(0)).to.equal(userA.address);
   expect(await dataCollection.ownerOf(1)).to.equal(userA.address);
   expect(await dataCollection.ownerOf(2)).to.equal(userB.address);
   expect(await dataCollection.ownerOf(3)).to.equal(userB.address);
   expect(await dataCollection.ownerOf(4)).to.equal(userB.address);
   ```

## Step 2: Credit Issuance

1. DEAR Foundation will make the rules on how many credits to award for each data contribution. Here just for illustration, we say that data 0, 2 and 3 are of good quality receiving two credits each, and data 1 just meets the bar receiving one credit, and data 4 is at an excellent quality receiving three credits. In total, User A will be awarded three credits and User B will be awarded seven credits:

   ```typescript
   await dearCoin.mint(userA.address, 3);
   await dearCoin.mint(userB.address, 7);
   ```

2. We can verify the credit balances of each user from the contract. We can also retrieve the total supply to be able to derive each user's share percentage:

   ```typescript
   expect(await dearCoin.balanceOf(userA.address)).to.equal(3);
   expect(await dearCoin.balanceOf(userB.address)).to.equal(7);
   expect(await dearCoin.totalSupply()).to.equal(10);
   ```

## Step 3: Dataset Organization

1. We will create two datasets available for users to subscribe to. The first will contain all those five pieces of data. The second will contain only the car data. Their URIs will point to a location specifying all the included data IDs.

   ```typescript
   await datasetCollection.mint(owner.address, 0, "https://raw.githubusercontent.com/comoco-labs/laicense/dev/dataset/0.json", []);
   await datasetCollection.mint(owner.address, 1, "https://raw.githubusercontent.com/comoco-labs/laicense/dev/dataset/1.json", []);
   ```

## Step 4: User Subscription

1. Let's say User C wants to access the second dataset of cars. User C will pay the subscription fee and request the license of that dataset. Here we assume that User C will pay 1000 USDT annually, and the current period ends on 01/01/2024, which converts to 1704096000 in unix timestamp. The on-chain Dataset Collection will then record the subscription information:

   ```typescript
   await datasetCollection.setUser(1, userC.address, 1704096000);
   ```

2. We can later verify the recorded expiration time for User C as well.

   ``` typescript
   expect(await datasetCollection.userExpires(1, userC.address)).to.equal(1704096000);
   ```

## Step 5: Profit Sharing

1. According to DEAR Foundation's guideline, the profit will be shared to the credit and data element holders. Let's assume we have no operating expense, so the net income is 1000 USDT.

2. A small portion (say 20% here) will be shared to the data element holders whose data directly contribute to the profit. Here we have User C paying subscription to access the dataset of cars, so the owners of those data are entitled to that portion of profit, which, in our demo, is just User B. So User B can claim:

   $$ 1000 \times 20\% = 200\,USDT $$

3. The remaining portion, which is the majority (80% here), will be shared to all the credit holders. Here we have User A holding 3 out of the total 10 credits, and User B holding 7 out of the total 10 credits. So User A can claim:

   $$ 1000 \times 80\% \times \frac{3}{10} = 240\,USDT $$

   User B can claim:

   $$ 1000 \times 80\% \times \frac{7}{10} = 560\,USDT $$

4. To sum it up, User A will claim $240\,USDT$ and User B will claim $200+560=760\,USDT$ altogether.

## Step 6: Model Publication

1. User C has the option of making the trained model public for commercial licensing to other applications. DEAR Foundation will record the usage statistics of the model to bill User C, and so will User C to other applications. In this case, the on-chain Model Collection will record the information and make User C the owner of the token representing the model:

   ```typescript
   await modelCollection.mint(userC.address, 0, "https://raw.githubusercontent.com/comoco-labs/laicense/dev/model/model.tflite", [{collection: DATASET_COLLECTION_ADDRESS, id: 1}]);
   ```

   Note that the model token also records what datasets the model is trained from, so that in the profit sharing phase we know whom to share with the small portion of the profit brought by this model as explained previously.

2. Likewise, we can verify the ownership later from the contract:

   ```typescript
   expect(await modelCollection.ownerOf(0)).to.equal(userC.address);
   ```

   We can also verify the datasets that the model is trained from:

   ```typescript
   const datasetTokens = await modelCollection.parentTokensOf(0);
   expect(datasetTokens).to.have.lengthOf(1);
   expect(datasetTokens[0].collection).to.equal(DATASET_COLLECTION_ADDRESS);
   expect(datasetTokens[0].id).to.equal(1);
   ```
