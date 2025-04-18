import { Box, Center, Editable, EditableInput, EditablePreview, Heading, Spinner, Text } from '@chakra-ui/react';
import { SignInButton, useUser } from '@clerk/clerk-react';
import { useBankDataContext } from '../../provider/BankDataProvider';



const Categories = () => {
    const { isSignedIn, isLoaded } = useUser();
    const { categories, isLoading } = useBankDataContext();

    if (!isLoaded && isLoading) {
        return (
            <Center h="100vh" axis='both'>
                <Heading color="navy" size="lg" marginRight={3}>
                    Loading
                </Heading>
                <Spinner
                    thickness='4px'
                    speed='0.65s'
                    emptyColor='gray.200'
                    color='navy'
                    size='lg'
                />
            </Center>
        );
    }
    else if (!isSignedIn) {
        return <Box>Sign in to view your categories  <SignInButton /></Box>;
    }
    else if (isSignedIn && !categories && !isLoading) {
        return (
            <Box>
                <Text>You have no category registered. Start by create a category: <button>Create an expense category</button></Text>
            </Box>
        );
    }
    else {
        return (
            <>
                {categories ? categories.map(cat => (
                    <Editable key={cat.category_id} defaultValue={cat.category_name}>
                        <EditablePreview />
                        <EditableInput />
                    </Editable>
                )) : "You have no categories yet."}
            </>
        );
    }
}

export default Categories;
