import { useUser } from '@clerk/clerk-react';
import axios from 'axios';
import { CreatableSelect } from 'chakra-react-select';
import { useState } from 'react';


const CategorySelector = ({ initialCategories = [], allCategories = ["Nourriture", "Transport", "Loisir"], handleOnChangeCategory }) => {
    const [categories, setCategories] = useState(initialCategories);
    const { user } = useUser();
    // const [selectedCategories, setSelectedCategories] = useState([]);

    const handleAddCategory = (category) => {
        setCategories([...categories, category]);

        axios.post('http://localhost:8000/categories', {
            category_name: category,
            category_description: "",
            user_id: user.id
        })
            .then((response) => {
                console.log(response.data);
                setCategories([...categories, response.data]);
            })
    };

    // const filteredCategories = allCategories.filter(category =>
    //     category.toLowerCase().includes(inputValue.toLowerCase()) && !categories.includes(category)
    // );
    // console.log(filteredCategories);

    return (
        <CreatableSelect
            isMulti
            name="categories"
            options={[
                {
                    label: "Categories",
                    options: allCategories.map(category => ({ value: category, label: category.category_name }))
                }
            ]}
            placeholder="Select some categories..."
            closeMenuOnSelect={false}
            defaultValue={categories.map(category => ({ value: category, label: category.category_name }))}
            onChange={handleOnChangeCategory}
            onCreateOption={handleAddCategory}
        />
    );
}

export default CategorySelector;
